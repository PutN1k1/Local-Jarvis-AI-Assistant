from pynput.keyboard import Key,Controller,GlobalHotKeys,Listener


class Music():
    def __init__(self):
        self.keyBoard = Controller()
        
        with GlobalHotKeys({
            '<left>': self.prev,
            '<right>': self.next,
            '<down>' : self.pause,
            '+' : self.inc_volume,
            '-' : self.dec_volume
            }) as threat:
            threat.join()
        
    def next(self):
        self.keyBoard.press(Key.media_next)
        self.keyBoard.release(Key.media_next)
        
    def prev(self):
        # Двойное нажатие для перехода именно на прошлый трек
        for _ in range(2):
            self.keyBoard.press(Key.media_previous)
            self.keyBoard.release(Key.media_previous)
        
    def replay(self):
        self.keyBoard.press(Key.media_previous)
        self.keyBoard.release(Key.media_previous)

    def pause(self):
        self.keyBoard.press(Key.media_play_pause)
        self.keyBoard.release(Key.media_play_pause)
        
    def inc_volume(self):
        self.keyBoard.press(Key.media_volume_up)
        self.keyBoard.release(Key.media_volume_up)
        
    def dec_volume(self):
        self.keyBoard.press(Key.media_volume_down)
        self.keyBoard.release(Key.media_volume_down)


muisc = Music()