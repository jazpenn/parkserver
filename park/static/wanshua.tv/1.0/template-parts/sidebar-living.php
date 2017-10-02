<div class="sidebar living-sidebar" id="video-sidebar">


  <!-- Nav tabs -->
  <ul class="nav nav-tabs" role="tablist" id="aside-header">
    <li role="presentation" class="active"><a href="#chat" aria-controls="chat" role="tab" data-toggle="tab">聊天</a></li>
    <li role="presentation"><a href="#board" aria-controls="board" role="tab" data-toggle="tab">土豪榜</a></li>
  </ul>

  <!-- Tab panes -->
  <div class="tab-content aside-tab-wrapper" id="aside-container">

    <div role="tabpanel" class="tab-pane active" id="chat">
      <div class="chat-list-wrapper">
        <div id="chatWindow" class="chat-list">
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">msg<img src="assets/images/gifts/hug.png" ></span></div>
          <div class="bubble"><span class="sender">李四</span>: <span class="msg">long message</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">ultra long message which can wrap at eighty percent </span></div>
          <div class="bubble player"><span class="sender">王五</span>: <span class="msg">lorem ipsum</span></div> <!-- 主播发送的消息 -->
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">very long message</span></div>
          <div class="bubble mine"><span class="sender">我</span>: <span class="msg">one more message</span></div> <!-- 当前用户发送的消息 -->
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
          <div class="bubble"><span class="sender">长长的用户名</span>: <span class="msg">another message</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">yet another message</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">very long message</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">one more message</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">another message</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">yet another message</span></div>
          <div class="bubble"><span class="sender">张三</span>: <span class="msg">lorem ipsum</span></div>
          <div id="nothing"></div> <!-- 在demo中，这一行不能删除，是用来插入新的聊天消息时判断位置的 -->
        </div>
        <div id="inputWindow" class="chat-input-field">
          <div class="error-note"><span>发送消息太频繁啦～</span></div>
          <input id="inp" type="text" />
          <input id="btn" type="button" value="发送" />
        </div>
      </div>
    </div>

    <div role="tabpanel" class="tab-pane" id="board">
      <ul>
        <li>
          <span class="player-rate">1</span>
          <span class="player-karma">14级</span>
          <span class="player-info">排行榜用户1</span>
        </li>
        <li>
          <span class="player-rate">2</span>
          <span class="player-karma">14级</span>
          <span class="player-info">排行榜用户1</span>
        </li>
        <li>
          <span class="player-rate">3</span>
          <span class="player-karma">14级</span>
          <span class="player-info">排行榜用户1</span>
        </li>
        <li>
          <span class="player-rate">4</span>
          <span class="player-karma">14级</span>
          <span class="player-info">排行榜用户1</span>
        </li>
        <li>
          <span class="player-rate">5</span>
          <span class="player-karma">14级</span>
          <span class="player-info">排行榜用户1</span>
        </li>
      </ul>
    </div>

  </div>

</div>


<script type="text/javascript">
  var btn   = document.getElementById('btn'),
    inp   = document.getElementById('inp'),
    chats = document.getElementById('chatWindow')
  ;
  btn.addEventListener('click', postMsg);

  inp.addEventListener('keyup', function(e) {
    if (e.keyCode == 13) { postMsg(); }
  });

  function postMsg() {
    var msg   = inp.value,
          bubble  = document.createElement('div'),
          p     = document.createElement('span');
      if (msg.trim().length <= 0) { return; }
      bubble.classList.add('bubble');
      bubble.classList.add('mine');
      p.textContent = msg;
      bubble.appendChild(p);
      inp.value = '';
      //chats.insertBefore(bubble, chats.firstChild);
      chats.insertBefore(bubble, chats.lastChild);

  }
</script>