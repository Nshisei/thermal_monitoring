import time
import threading
try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class CameraEvent(object):
    """An Event-like class that signals all active clients when a new frame is
    available.
    """
    def __init__(self):
        self.events = {}

    def wait(self):
        """Invoked from each client's thread to wait for the next frame."""
        ident = get_ident()
        if ident not in self.events:
            # this is a new client
            # add an entry for it in the self.events dict
            # each entry has two elements, a threading.Event() and a timestamp
            self.events[ident] = [threading.Event(), time.time()]
        return self.events[ident][0].wait()

    def set(self):
        """Invoked by the camera thread when a new frame is available."""
        now = time.time()
        remove = []
        for ident, event in self.events.items():
            if not event[0].isSet():
                # if this client's event is not set, then set it
                # also update the last set timestamp to now
                event[0].set()
                event[1] = now
            else:
                # if the client's event is already set, it means the client
                # did not process a previous frame
                # if the event stays set for more than 5 seconds, then assume
                # the client is gone and remove it
                if now - event[1] > 5:
                    remove.append(ident)

        for ident in remove:        
            del self.events[ident]

    def clear(self):
        """Invoked from each client's thread after a frame was processed."""
        self.events[get_ident()][0].clear()

class BaseCamera:
    """カメラの基本クラス。各サブクラスは独自のクラス変数を持ちます。"""
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.thread = None
        cls.frame = None
        cls.last_access = 0
        cls.event = CameraEvent()

    def __init__(self):
        """バックグラウンドのカメラスレッドを開始します。"""
        if self.__class__.thread is None:
            self.__class__.last_access = time.time()
            self.__class__.thread = threading.Thread(target=self._thread)
            self.__class__.thread.daemon = True
            self.__class__.thread.start()
            self.__class__.event.wait()

    def get_frame(self):
        """現在のカメラフレームを返します。"""
        self.__class__.last_access = time.time()
        self.__class__.event.wait()
        self.__class__.event.clear()
        return self.__class__.frame

    @staticmethod
    def frames():
        """カメラからフレームを返すジェネレータ。サブクラスで実装が必要です。"""
        raise NotImplementedError('サブクラスで実装してください。')

    @classmethod
    def _thread(cls):
        """カメラのバックグラウンドスレッド。"""
        print(f'{cls.__name__} スレッドを開始します。')
        frames_iterator = cls.frames()
        for frame in frames_iterator:
            cls.frame = frame
            cls.event.set()
            time.sleep(0)
            if time.time() - cls.last_access > 10:
                frames_iterator.close()
                print(f'{cls.__name__} スレッドを停止します。')
                break
        cls.thread = None