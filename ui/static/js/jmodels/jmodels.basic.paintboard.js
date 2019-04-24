/**
 * 画板对象
 * @param dom_id: Canvas DOM ID
 * @param width: 画板宽度
 * @param height: 画板高度
 * @param options: 画板选项
 * */
let JPaintbord = function (dom_id, width, height, options, profile) {
    this._id_pool = 1;
    this.id = 1;
    this.dom_id = dom_id;
    this.x = 0;
    this.y = 0;
    this.width = width;
    this.height = height;
    this.options = options;
    this.editor = undefined;
    this.profile = profile;

    this.name = profile.name;
    this.id = profile.id;
    this.flush_background_color = profile.background_color ? profile.background_color : "#eeeeee";
    this.background_color = this.flush_background_color;

    // 请求重绘次数
    this.commit_counter = 0;

    this.master = window.document.getElementById(this.dom_id).getContext('2d');
    this.dom = window.document.getElementById(this.dom_id);
    this.dom.painter = this;

    // 隐藏用于后端绘制
    let slave = document.createElement('canvas');
    slave.id = this.dom_id + '_shadow';
    slave.style.visibility = "hidden";
    this.slave = slave.getContext('2d');

    // 将主从画板设置为同样大小，方便进行图形拷贝
    this.slave.canvas.width = this.master.canvas.width = this.width;
    this.slave.canvas.height = this.master.canvas.height = this.height;

    // 图片库文件
    this.image_libraries_list = {};
    // 链接, 最下层
    this.links_list = {};
    // 锚点, 中间层
    this.anchors_list = {};
    // 模型， 最上层
    this.models_list = {};

    /*
    * 选择slave画板
    * */
    this.begin = function () {
        this.ctx = this.slave;
    };

    /**
     * 为了避免图像闪烁，将slave画板的内容一次性拷贝到master画板
     * */
    this.update = function () {
        //this.master.clearRect(0, 0, this.width, this.height);
        //this.master.fillRect(0, 0, this.width, this.height);
        this.master.drawImage(this.slave.canvas, 0, 0);
    };

    this.dom.onmousemove = function (ev) {
        return this.painter.editor && this.painter.editor.onmousemove ? this.painter.editor.onmousemove(ev) : this.painter.onmousemove(ev);
    };
    this.dom.onmousedown = function (ev) {
        return this.painter.editor && this.painter.editor.onmousedown ? this.painter.editor.onmousedown(ev) : this.painter.onmousedown(ev);
    };
    this.dom.onmouseup = function (ev) {
        return this.painter.editor && this.painter.editor.onmouseup ? this.painter.editor.onmouseup(ev) : this.painter.onmouseup(ev);
    };
    this.dom.onclick = function (ev) {
        return this.painter.onclick(ev);
    };
    this.dom.ondblclick = function (ev) {
        this.painter.ondblclick(ev);
    };

    /*模型事件监听器*/
    this.model_event_listener = new JEventListener(this);
    /*锚点事件监听器*/
    this.anchor_event_listener = new JEventListener(this);
    /*连接线事件监听器*/
    this.link_event_listener = new JEventListener(this);
    /*空白事件监听器*/
    this.empty_event_listener = new JEventListener(this);

    // 添加动画支持
    window.painter = this;
    window.requestAnimationFrame(for_JPaintboard_animate);

    // 预先从配置选项中加载对象
    return this.load(options.width, options.height, options.models, options.anchors, options.links, options.libraries);
};


// 将data字典中的数据更新到模型中
JPaintbord.prototype.update_all_model_value = function(data) {
    for (let id in data) {
        let model = this.search_model(id);

        if (model && data.hasOwnProperty(id)) {
            model.set_value(data[id])
        }
    }
};


JPaintbord.prototype.onmousemove = function(ev) {
    let anchor = this.select_anchor(ev);
    if (anchor) {
        return this.anchor_event_listener.probe_mousemove(ev, anchor);
    }

    let link = this.select_link(ev);
    if (link) {
        return this.link_event_listener.probe_mousemove(ev, link);
    }

    let model = this.select_model(ev);
    // 无论如何都向事件处理器发送光标移动事件，用于处理管标移入和移出事件
    this.model_event_listener.probe_mousemove(ev, model);

    if (!model) {
        // 没有找到任何可以派发消息的对象时，派发一条消息给空消息监听器列表，用于清楚状态
        return this.empty_event_listener.dispatch_mousemove_message(ev, this);
    }
};

JPaintbord.prototype.onmousedown = function(ev) {
    let anchor = this.select_anchor(ev);
    if (anchor) {
        return this.anchor_event_listener.dispatch_mousedown_message(ev, anchor);
    }

    let link = this.select_link(ev);
    if (link) {
        return this.link_event_listener.dispatch_mousedown_message(ev, link);
    }

    let model = this.select_model(ev);
    if (model) {
        return this.model_event_listener.dispatch_mousedown_message(ev, model);
    } else {
        // 没有找到任何可以派发消息的对象时，派发一条消息给空消息监听器列表，用于清楚状态
        return this.empty_event_listener.dispatch_mousedown_message(ev, this);
    }
};

JPaintbord.prototype.onmouseup = function(ev) {
    let anchor = this.select_anchor(ev);
    if (anchor) {
        return this.anchor_event_listener.dispatch_mouseup_message(ev, anchor);
    }

    let link = this.select_link(ev);
    if (link) {
        return this.link_event_listener.dispatch_mouseup_message(ev, link);
    }

    let model = this.select_model(ev);
    if (model) {
        return this.model_event_listener.dispatch_mouseup_message(ev, model);
    } else {
        // 没有找到任何可以派发消息的对象时，派发一条消息给空消息监听器列表，用于清楚状态
        return this.empty_event_listener.dispatch_mouseup_message(ev, this);
    }
};

JPaintbord.prototype.onclick = function(ev) {
    let anchor = this.select_anchor(ev);
    if (anchor) {
        return this.anchor_event_listener.dispatch_click_message(ev, anchor);
    }

    let link = this.select_link(ev);
    if (link) {
        return this.link_event_listener.dispatch_click_message(ev, link);
    }

    let model = this.select_model(ev);
    if (model) {
        return this.model_event_listener.dispatch_click_message(ev, model);
    } else {
        // 没有找到任何可以派发消息的对象时，派发一条消息给空消息监听器列表，用于清楚状态
        return this.empty_event_listener.dispatch_click_message(ev, this);
    }
};

JPaintbord.prototype.ondblclick = function(ev) {
    let anchor = this.select_anchor(ev);
    if (anchor) {
        return this.anchor_event_listener.dispatch_dblclick_message(ev, anchor);
    }

    let link = this.select_link(ev);
    if (link) {
        return this.link_event_listener.dispatch_dblclick_message(ev, link);
    }

    let model = this.select_model(ev);
    if (model) {
        return this.model_event_listener.dispatch_dblclick_message(ev, model);
    } else {
        // 没有找到任何可以派发消息的对象时，派发一条消息给空消息监听器列表，用于清楚状态
        return this.empty_event_listener.dispatch_dblclick_message(ev, this);
    }
};


/**
 * 提交一次重回请求
 * */
JPaintbord.prototype.commit = function () {
    this.commit_counter += 1;
};


let speed = 0;
function for_JPaintboard_animate() {
    if ( speed ++ % 20 ) {
        window.requestAnimationFrame(for_JPaintboard_animate);
        return;
    }
    let painter = window.painter;
    //if ( painter.commit_counter > 0 ) {
        painter.begin();
        painter.render();
        painter.update();
        painter.commit_counter = 0;
    //}
    window.requestAnimationFrame(for_JPaintboard_animate)
}


/**
 * 开始执行动画渲染，可能会增加能耗
 * */
JPaintbord.prototype.animate = function() {
};


JPaintbord.prototype.render_all_links = function (ctx) {
    for (let i in this.links_list) {
        //console.log(this.links_list[i]);
        this.links_list[i].render && this.links_list[i].render(ctx);
    }
};

JPaintbord.prototype.render_all_anchors = function (ctx) {
    for (let i in this.anchors_list) {
        //console.log(this.anchors_list[i]);
        this.anchors_list[i].render && this.anchors_list[i].render(ctx);
    }
};

JPaintbord.prototype.render_all_models = function (ctx) {
    for (let i in this.models_list) {
        //console.log(this.models_list[i]);
        this.models_list[i].render && this.models_list[i].render(ctx);
    }
};

JPaintbord.prototype.render_background = function (ctx) {
    //ctx.clearRect(0, 0, this.width, this.height);
    ctx.fillStyle = this.flush_background_color;
    ctx.fillRect(0, 0, this.width, this.height);
    ctx.strokeRect(this.x, this.y, this.width, this.height);
};


/**
 * 将元素全都一次性绘制到slave画板上
 * 注意渲染顺序为:
 *   Link --->   anchor  ---> model
 *  这个顺序在编辑器中有编辑关联性
 * */
JPaintbord.prototype.render = function () {
    let ctx = this.ctx;
    if ( this.editor ) {
        this.editor.render(ctx);
    } else {
        // 清空画布
        this.render_background(ctx);
        this.render_all_links(ctx);
        this.render_all_anchors(ctx);
        this.render_all_models(ctx);
    }
};

/**
 * 通过具体的数据加载模型
 * */
JPaintbord.prototype.load_model = function(id, profile) {
    this.models_list[id] = new JModel(id, this, profile);
    this._id_pool = this._id_pool > id ? this._id_pool : id;
    return this.models_list[id];
};

/**
 * 通过具体数据加载链接
 * */
JPaintbord.prototype.load_link = function(id, begin, end, style) {
    this.links_list[id] = new JLink(id, begin, end, style);
    this._id_pool = this._id_pool > id ? this._id_pool : id;
    return this.links_list[id];
};

/**
 * 通过具体数据加载锚点
 * */
JPaintbord.prototype.load_anchor = function(id, model, profile) {
    this.anchors_list[id] = new JAnchor(id, model, profile);
    this._id_pool = this._id_pool > id ? this._id_pool : id;
    return this.anchors_list[id];
};

/**
 * 通过具体数据加载图片库
 * */
JPaintbord.prototype.load_image_library = function(id, name, src, row, column, unit_width, unit_height) {
    this.image_libraries_list[id] = new JLibrary(id, name, src, row, column, unit_width, unit_height);
    this._id_pool = this._id_pool > id ? this._id_pool : id;
    return this.image_libraries_list[id];
};

/**
 * 从JSON对象加载全部模型、锚点、链接
 * 作为一种例行任务，返回对象本身
 * width，height 可以让对象的位置进行等比例适配
 * */
JPaintbord.prototype.load = function(width, height, models, anchors, links, libraries) {
    if ( libraries ) {
        for ( let i = 0, len = libraries.length; i < len; i ++ ) {
            let l = libraries[i];
            this.load_image_library(l.id, l.name, l.src, l.row, l.column, l.unit_width, l.unit_height);
        }
    }

    if ( models ) {
        let x_zoom_index = (true === true ? 1 : this.width / width);
        let y_zoom_index = (true === true ? 1 : this.height / height);
        for ( let i = 0, len = models.length; i < len; i ++ ) {
            let m = models[i];
            this.load_model(m.id, m);
        }
    }

    if ( anchors ) {
        for ( let i = 0, len = anchors.length; i < len; i ++ ) {
            let profile = anchors[i];
            let model = this.search_model(profile.model);
            this.load_anchor(profile.id, model, profile);
        }
    }

    if ( links ) {
        for ( let i = 0, len = links.length; i < len; i ++ ) {
            let l = links[i];
            let begin_anchor = this.search_anchor(l.begin);
            let end_anchor = this.search_anchor(l.end);
            this.load_link(l.id, begin_anchor, end_anchor, l);
        }
    }

    return this;
};

/**
 * 根据鼠标事件选择模型
 * */
JPaintbord.prototype.select_model = function (ev) {
    for ( let id in this.models_list ) {
        if ( !this.models_list.hasOwnProperty(id) ) {
            continue;
        }
        let model = this.models_list[id];
        if ( model.is_cursor_in(ev) ) {
            return model;
        }
    }

    return null;
};


/**
 * 根据鼠标事件选择锚点
 * */
JPaintbord.prototype.select_anchor = function (ev) {
    for ( let id in this.anchors_list ) {
        if ( !this.anchors_list.hasOwnProperty(id) ) {
            continue;
        }
        let anchor = this.anchors_list[id];
        if ( anchor.is_cursor_in(ev) ) {
            return anchor;
        }
    }

    return null;
};


/**
 * 根据鼠标事件选择连接线
 * */
JPaintbord.prototype.select_link = function (ev) {
    for ( let id in this.links_list ) {
        if ( !this.links_list.hasOwnProperty(id) ) {
            continue;
        }
        let link = this.links_list[id];
        if ( link.is_cursor_in(ev) ) {
            return link;
        }
    }

    return null;
};


/**
 * 根据ID搜索模型
 * */
JPaintbord.prototype.search_model = function (id) {
    return this.models_list[id];
};
JPaintbord.prototype.search_model_by_id = JPaintbord.prototype.search_model;
JPaintbord.prototype.search_model_by_name = function(name) {
    for (let key in this.models_list) {
        let model = this.models_list[key];
        if (model.name === name) {
            return model;
        }
    }
    return null;
};

/**
 * 根据ID搜索链接
 * */
JPaintbord.prototype.search_link = function (id) {
    return this.links_list[id];
};
JPaintbord.prototype.search_link_by_id = JPaintbord.prototype.search_link;
JPaintbord.prototype.search_link_by_name = function(name) {};

// 返回第一条被搜索到的link
JPaintbord.prototype.search_link_by_anchor_object = function(anchor) {
    for (let id in this.links_list) {
        if (this.links_list[id].begin === anchor) {
            return this.links_list[id];
        }

        if (this.links_list[id].end === anchor) {
            return this.links_list[id];
        }
    }

    return null;
};


/**
 * 根据ID搜索锚点
 * */
JPaintbord.prototype.search_anchor = function (id) {
    return this.anchors_list[id];
};
JPaintbord.prototype.search_anchor_by_id = JPaintbord.prototype.search_anchor;
JPaintbord.prototype.search_anchor_by_name = function(name) {};
JPaintbord.prototype.search_anchors_by_model = function(id) {
    let anchors = [];
    for (let i in this.anchors_list) {
        if (this.anchors_list.hasOwnProperty(i) && this.anchors_list[i].model.id === id) {
            anchors.push(this.anchors_list[i]);
        }
    }
    return anchors;
};

/**
 * 根据ID搜索图片库
 * */
JPaintbord.prototype.search_image_library = function (id) {
    return this.image_libraries_list[id];
};
JPaintbord.prototype.search_image_library_by_id = JPaintbord.prototype.search_image_library;
JPaintbord.prototype.search_image_library_by_name = function(name) {
    for ( let idx in this.image_libraries_list ) {
        if ( ! this.image_libraries_list.hasOwnProperty(idx) ) {
            continue;
        }

        let library = this.image_libraries_list[idx];
        if ( library.name !== name ) {
            continue;
        }
        return library;
    }
    return undefined;
};

/**
 * 判断两个锚点是否是连接的
 * */
JPaintbord.prototype.is_linked = function (a, b) {
    let test_list = [a, b];

    for ( let idx in this.links_list) {
        if (!this.links_list.hasOwnProperty(idx)) {
            continue;
        }
        let link = this.links_list[idx];
        if ( test_list.indexOf(link.end) >= 0 && test_list.indexOf(link.begin) >= 0 ) {
            return link;
        }
    }

    return undefined;
};
