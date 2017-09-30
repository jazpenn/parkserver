from blinker import Namespace

signals = Namespace()

rate_update = signals.signal('rate-update')

like_content = signals.signal('like-content')

reply_content = signals.signal('reply-content')

add_post = signals.signal('add-post')



