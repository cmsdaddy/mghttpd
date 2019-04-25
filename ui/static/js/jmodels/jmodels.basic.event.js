/**
 * Jmodels的对象事件监听对象
 * */

let JEventListener = function(painter) {
    // 绘图对象
    this.painter = painter;
    // 最后一次被激活的对象
    this._last_object = null;

    // 光标移动事件
    this._onmousemove_callback_list = [];
    // 左键按下事件
    this._onmousedown_callback_list = [];
    // 左键弹起事件
    this._onmouseup_callback_list = [];
    // 光标移出事件
    this._onmousein_callback_list = [];
    // 光标移出事件
    this._onmouseout_callback_list = [];
    // 鼠标左键单击事件
    this._onclick_callback_list = [];
    // 鼠标左键双击事件
    this._ondblclick_callback_list = [];
    return this;
};


/*用于处理光标移动事件*/
JEventListener.prototype.probe_mousemove = function(ev, obj) {
    if (!obj) {
        // 光标移动时没有找到对象，可能发送光标离开的事件
        if (this._last_object) {
            this.dispatch_mouseout_message(ev, this._last_object);
            this._last_object = obj;
        }
    } else {
        if (this._last_object) {
            // 前一状态已经在对象内部
            if (obj === this._last_object) {
                // 同一对象发送mousemove事件
                this.dispatch_mousemove_message(ev, obj);
            } else {
                // 不同对象时，旧对象发送mouseout事件，新对象发送mousein事件
                this.dispatch_mouseout_message(ev, this._last_object);
                this._last_object = obj;
                this.dispatch_mousein_message(ev, obj);
            }
        } else {
            // 前一状态不在对象内部，发送mousein事件
            this._last_object = obj;
            this.dispatch_mousein_message(ev, obj);
        }
    }
};


/*用于将obj上的ev消息派发到list中*/
JEventListener.prototype.dispatch_message = function(ev, obj, list) {
    let length = list.length;

    for (let i =0; i < length; i ++ ) {
        list[i](ev, obj);
    }

    return this;
};

// 光标移动事件回调注册
JEventListener.prototype.onmousemove = function (callback) {
    this._onmousemove_callback_list.push(callback);
    return this;
};
// 派发光标移动事件
JEventListener.prototype.dispatch_mousemove_message = function(ev, obj) {
    return this.dispatch_message(ev, obj, this._onmousemove_callback_list);
};


// 左键按下事件回调注册
JEventListener.prototype.onmousedown = function (callback) {
    this._onmousedown_callback_list.push(callback);
    return this;
};
// 派发左键按下事件
JEventListener.prototype.dispatch_mousedown_message = function(ev, obj) {
    return this.dispatch_message(ev, obj, this._onmousedown_callback_list);
};


// 左键弹起事件回调注册
JEventListener.prototype.onmouseup = function (callback) {
    this._onmouseup_callback_list.push(callback);
    return this;
};
// 派发左键弹起事件
JEventListener.prototype.dispatch_mouseup_message = function(ev, obj) {
    return this.dispatch_message(ev, obj, this._onmouseup_callback_list);
};


// 光标移入事件回调注册
JEventListener.prototype.onmousein = function (callback) {
    this._onmousein_callback_list.push(callback);
    return this;
};
// 派发光标移入事件
JEventListener.prototype.dispatch_mousein_message = function(ev, obj) {
    return this.dispatch_message(ev, obj, this._onmousein_callback_list);
};


// 光标移出事件回调注册
JEventListener.prototype.onmouseout = function (callback) {
    this._onmouseout_callback_list.push(callback);
    return this;
};
// 派发光标移出事件
JEventListener.prototype.dispatch_mouseout_message = function(ev, obj) {
    return this.dispatch_message(ev, obj, this._onmouseout_callback_list);
};


// 鼠标左键单击事件回调注册
JEventListener.prototype.onclick = function (callback) {
    this._onclick_callback_list.push(callback);
    return this;
};
// 派发光标移动事件
JEventListener.prototype.dispatch_click_message = function(ev, obj) {
    return this.dispatch_message(ev, obj, this._onclick_callback_list);
};


// 鼠标左键双击事件回调注册
JEventListener.prototype.ondblclick = function (callback) {
    this._ondblclick_callback_list.push(callback);
    return this;
};
// 派发左键双击事件
JEventListener.prototype.dispatch_dblclick_message = function(ev, obj) {
    return this.dispatch_message(ev, obj, this._ondblclick_callback_list);
};
