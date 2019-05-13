let ClickSelectStack = function(obj) {
    // 选择的模型
    this.models = [];
    // 选择的连接
    this.links = [];
    // 选择的锚点
    this.anchors = [];

    // 光标位置
    this.cursor = [];
};

// 清空所有选择的对象
ClickSelectStack.prototype.empty = function() {
    this.models = [];
    this.links = [];
    this.anchors = [];
    this.cursor = [];
};
// 激活节点选择
ClickSelectStack.prototype.active_models = function() {
    this.links = [];
    this.anchors = [];
    this.cursor = [];
};
// 激活连接选择
ClickSelectStack.prototype.active_links = function() {
    this.models = [];
    this.anchors = [];
    this.cursor = [];
};


let jDomMask = function(painter) {
    // 绘制位置的父节点
    this.parent = painter.dom.parentNode;

    // 创建一个字符绘制蒙版
    this.dom = document.createElement('div');
    this.dom.id = painter.dom_id + '_text';
    this.parent.appendChild(this.dom);

    let text_dom_style = "display: block; position: absolute; float: left; ";

    text_dom_style += "top: " + painter.master_dom.offsetTop + 'px;';
    text_dom_style += "left: " + painter.master_dom.offsetLeft + 'px;';
    text_dom_style += "width: " + painter.size.get_width() + "px;";
    text_dom_style += "height: " + painter.size.get_height() + 'px;';
    text_dom_style += "border: black solid 1px;";

    this.dom.style.cssText = text_dom_style;

    // 新建的dom对象
    this.doms = {};
};
jDomMask.prototype.create_edit_box_for_model = function(id, text) {
    if (this.doms.hasOwnProperty(id)) {
        this.doms[id].innerText = text;
    }
};


/**
 * jmodels 的模型对象编辑器
 * 主要功能：
 *  - 绘制参考线
 *  - 绘制锚点
 *  - 绘制模型
 *  - 连接锚点
 *  - 修改模型位置
 *  - 修改模型大小
 * */
let JEditor = function (painter) {
    this.painter = painter;
    this.painter.editor = this;

    // 光标在模型修改大小象限
    this.in_resize_model_arae = false;
    // 光标在模型移动位置象限
    this.in_move_model_arae = false;

    // 选择的模型
    this.model_selected = undefined;

    // 选择的锚点栈, 左键按下选择，左键弹起清空
    this.anchor_stack_selected = [];
    // 动态显示的锚点, 光标移动到锚点上时可以高亮显示，光标移入范围选择，移出范围清空
    this.hot_anchors_stack = [];
    // 跟随光标移动的线，选择锚点时激活，光标移动时更新，左键弹起时清空
    this.hotlines_stack = [];
    // 改变大小的对象选择栈，左键点击对象的第四象限时选择，光标移动时更新，左键弹起时清空
    this.resize_models_stack = [];
    // 改变位置的对象选择栈，左键点击对象的第一、二、三象限时选择，光标移动时更新，左键弹起时清空
    this.change_location_models_statck = [];
    // 选择的模型基本属性栈，选择时压入，左键弹起时清空
    this.attribute_of_selected_model_statck = {};
    // 光标移动的位置记录, 左键按下时记录，左键弹起时清空
    this.cursor_motion_stack = [];

    // 点击选择列表
    this.select_stack = new ClickSelectStack(this);
    // 光标拖拽选择栈，左键按下时记录，弹起时清空，移动时更新第二个记录
    this.area_selection_stack = [];

    // 开始移动的点
    this.move_begin_point = undefined;

    // 可编辑的最小模型宽度
    this.model_min_width = 30;
    // 可编辑的最小模型高度
    this.model_min_height = 30;

    window.requestAnimationFrame(this.animation_render);
    window.editor = this;

    this._onlink = [];
    this.onlink = function (callback) {
        if (this._onlink.indexOf(callback) === -1) {
            this._onlink.push(callback);
        }
    };
    this.notify_link = function (link, begin, end) {
        let length = this._onlink.length;
        for (let i = 0; i < length; i ++) {
            this._onlink[i](this, link, begin, end)
        }
    };

    // 编辑区空白处点击事件, 点击空白区域后清空选择栈中的全部对象
    //painter.empty_event_listener.onmousedown(this.select_stack.empty);

    //this.dom_mask = new jDomMask(painter);
    return this;
};


// 删除所选
JEditor.prototype.delete_selected = function() {
    let length = this.select_stack.models.length;
    for (let i = 0; i < length; i ++) {
        let model = this.select_stack.models[i];

        for (let aid in this.painter.anchors_list) {
            if (this.painter.anchors_list.hasOwnProperty(aid)) {
                let anchor = this.painter.anchors_list[aid];
                if (anchor.model !== model) {
                    continue;
                }

                while (true) {
                    let link = this.painter.search_link_by_anchor_object(anchor);
                    if (link) {
                        delete this.painter.links_list[link.id];
                        console.log("delete relation link:", link);
                    } else {
                        break;
                    }
                }

                console.log("delete relation anchor:", anchor);
                delete this.painter.anchors_list[anchor.id];
            }
        }

        console.log("delete model:", model);
        delete this.painter.models_list[model.id];
    }

    length = this.select_stack.links.length;
    for (let i = 0; i < length; i ++) {
        let link = this.select_stack.links[i];
        for (let lid in this.painter.links_list) {
            if (this.painter.links_list.hasOwnProperty(lid)) {
                let target = this.painter.links_list[lid];
                if (target.id === link.id) {
                    console.log("delete link:", target);
                    delete this.painter.links_list[lid];
                    break;
                }
            }
        }
    }

    this.select_stack.empty();
};
JEditor.prototype.copy_select_model = function(){
    let length = this.select_stack.models.length;
    let profiles = [];
    for (let i = 0; i < length; i ++) {
        let model = this.select_stack.models[i];
        let p = model.save();
        profiles.push(p);
    }
    return profiles;
};
JEditor.prototype.align_left = function(){
};
JEditor.prototype.align_right = function(){
};
JEditor.prototype.align_h_center = function(){
    let length = this.select_stack.models.length;
    let stander = null;
    for (let i = 0; i < length; i ++) {
        let model = this.select_stack.models[i];
        if (i === 0) {
            stander = model;
            continue;
        }
        this.update_model_location(model, model.x_offset, stander.y_offset);
    }
};
JEditor.prototype.align_v_center = function(){
    let length = this.select_stack.models.length;
    let stander = null;
    for (let i = 0; i < length; i ++) {
        let model = this.select_stack.models[i];
        if (i === 0) {
            stander = model;
            continue;
        }
        this.update_model_location(model, stander.x_offset, model.y_offset);
    }
};
JEditor.prototype.same_size = function(){
    let length = this.select_stack.models.length;
    let stander = null;
    for (let i = 0; i < length; i ++) {
        let model = this.select_stack.models[i];
        if (i === 0) {
            stander = model;
            continue;
        }
        this.update_model_size(model, stander.width, stander.height);
    }
};
JEditor.prototype.eq_v_distance = function(){
    let length = this.select_stack.models.length;
    if (length < 3) {
        return;
    }
    this.select_stack.models.sort(function (a, b) {
        return a.y_offset - b.y_offset;
    });

    let min_y_offset = this.select_stack.models[0].y_offset;
    let max_y_offset = this.select_stack.models[length-1].y_offset;

    if (max_y_offset - min_y_offset < 1) {
        return;
    }

    let distance = (max_y_offset - min_y_offset) / (length -1);
    let new_y_offset = min_y_offset + distance;
    for (let i = 1; i < length - 1; i ++, new_y_offset += distance) {
        let model = this.select_stack.models[i];
        this.update_model_location(model, model.x_offset, new_y_offset);
    }
};
JEditor.prototype.eq_h_distance = function(){
    let length = this.select_stack.models.length;
    if (length < 3) {
        return;
    }
    this.select_stack.models.sort(function (a, b) {
        return a.x_offset - b.x_offset;
    });

    let min_x_offset = this.select_stack.models[0].x_offset;
    let max_x_offset = this.select_stack.models[length-1].x_offset;

    if (max_x_offset - min_x_offset < 1) {
        return;
    }

    let distance = (max_x_offset - min_x_offset) / (length -1);
    let new_x_offset = min_x_offset + distance;
    for (let i = 1; i < length - 1; i ++, new_x_offset += distance) {
        let model = this.select_stack.models[i];
        this.update_model_location(model, new_x_offset, model.y_offset);
    }
};
JEditor.prototype.toggle_boarder = function(){
    let length = this.select_stack.models.length;
    for (let i = 0; i < length; i ++) {
        let model = this.select_stack.models[i];
        model.show_boarder = !model.show_boarder;
    }
};


JEditor.prototype.animation_render = function() {
    console.log(this.editor);
};


/**
 * 绘制编辑模式下的连接线补充内容
 * */
JEditor.prototype.render_link = function(ctx, link) {
};


/**
 * 绘制编辑模式下的锚点补充内容
 * */
JEditor.prototype.render_anchor = function(ctx, anchor) {
    ctx.save();
    //ctx.strokeRect(anchor.x, anchor.y, anchor.width, anchor.height);
    ctx.fillStyle = '#23ca57';
    ctx.fillRect(anchor.x, anchor.y, anchor.width, anchor.height);
    ctx.fillText(anchor.id, anchor.x, anchor.y);
    ctx.restore();
};


/**
 * 绘制编辑模式下的模型补充内容
 * */
JEditor.prototype.render_model = function(ctx, model) {
    // 绘制调整大小的把手

    let x = model.x_offset + model.width/2;
    let y = model.y_offset + model.height/2;

    ctx.save();

    ctx.beginPath();
    for ( let i = 1; i <= 4; i ++) {
        ctx.moveTo(x - 5 * i, y);
        ctx.lineTo(x, y - 5 * i);
    }
    ctx.stroke();
    ctx.restore();
    /*
    ctx.fillText("id:"+model.id, model.x_offset - 30, model.y_offset - 10);
    ctx.fillText("x:"+model.x, model.x_offset - 30, model.y_offset - 22);
    ctx.fillText("y:"+model.y, model.x_offset - 30, model.y_offset - 34);
    ctx.fillText("W:"+model.width, model.x_offset - 30, model.y_offset - 46);
    ctx.fillText("H:"+model.height, model.x_offset - 30, model.y_offset - 58);
    */
};


/**
 * 绘制编辑区的参考线
 * */
JEditor.prototype.render_reference_grid = function(ctx) {
    let width = this.painter.width;
    let height = this.painter.height;
    let color_deep = "#CCCCCC";
    let color_light = "#DDDDDD";

    ctx.save();

    for (let x = 10; x < width; x += 10) {
        let color = x % 50 ? color_light : color_deep;
        ctx.beginPath();
        ctx.moveTo(x+0.5, 0);
        ctx.lineTo(x+0.5, height);
        ctx.strokeStyle = color;
        ctx.stroke();
    }

    for (let x = 10; x < width; x += 10) {
        let color = x % 50 ? color_light : color_deep;
        ctx.beginPath();
        ctx.moveTo(0, x + 0.5);
        ctx.lineTo(width, x + 0.5);
        ctx.strokeStyle = color;
        ctx.stroke();
    }

    ctx.restore();
};


/**
 * 编辑器的绘制事件
 * */
JEditor.prototype.render = function(ctx) {
    ctx.save();

    this.painter.render_background(ctx);

    // 绘制参考线
    this.render_reference_grid(ctx);

    this.painter.render_all_links(ctx);
    this.painter.render_all_anchors(ctx);
    this.painter.render_all_models(ctx);

    // 绘制连接线
    let link_list = this.painter.links_list;
    for (let idx in link_list) {
        if ( ! link_list.hasOwnProperty(idx) ) {
            continue;
        }
        this.render_link(ctx, link_list[idx]);
    }

    // 绘制锚点
    let anchor_list = this.painter.anchors_list;
    for (let idx in anchor_list) {
        if ( ! anchor_list.hasOwnProperty(idx) ) {
            continue;
        }
        this.render_anchor(ctx, anchor_list[idx]);
    }

    // 绘制模型
    let model_list = this.painter.models_list;
    for (let idx in model_list) {
        if ( ! model_list.hasOwnProperty(idx) ) {
            continue;
        }
        this.render_model(ctx, model_list[idx]);
    }

    // 绘制热锚点
    for ( let idx in this.hot_anchors_stack ) {
        if ( !this.hot_anchors_stack.hasOwnProperty(idx) ) {
            continue;
        }
        let anchor = this.hot_anchors_stack[idx];
        ctx.save();
        ctx.strokeStyle = 'blue';
        ctx.strokeRect(anchor.x - 3 - 0.5, anchor.y - 3 - 0.5, anchor.width + 3 * 2, anchor.height + 3 * 2);
        ctx.stroke();
        ctx.restore();
    }

    // 绘制热线
    ctx.save();
    ctx.strokeStyle = 'blue';
    for ( let idx in this.hotlines_stack ) {
        if ( !this.hotlines_stack.hasOwnProperty(idx) ) {
            continue;
        }
        let hot_line = this.hotlines_stack[idx];
        ctx.moveTo(hot_line.begin_x, hot_line.begin_y);
        ctx.lineTo(hot_line.end_x, hot_line.end_y);
        ctx.stroke();
    }
    ctx.restore();

    // 绘制加入选区的模型
    for (let i = 0, length = this.select_stack.models.length; i < length; i ++) {
        let model = this.select_stack.models[i];
        ctx.strokeStyle = '#ff00ff';
        ctx.strokeRect(model.x - 5, model.y - 5, model.width + 10, model.height + 10);
    }

    // 绘制加入选区的连接
    ctx.save();
    ctx.strokeStyle = '#3bff28';
    ctx.lineWidth = 3;
    for (let i = 0, length = this.select_stack.links.length; i < length; i ++) {
        let link = this.select_stack.links[i];

        ctx.moveTo(link.begin.x + link.begin.width/2, link.begin.y + link.begin.height/2);
        ctx.lineTo(link.end.x + link.end.width/2, link.end.y + link.end.height/2);
        ctx.stroke();
    }
    ctx.restore();

    // 绘制选择的模型, 有改变模型位置的选择对象
    for(let i = 0, length = this.change_location_models_statck.length; i < length; i ++) {
        let model = this.change_location_models_statck[i];
        ctx.strokeStyle = 'red';
        ctx.strokeRect(model.x - 5, model.y - 5, model.width + 10, model.height + 10);
    }

    // 绘制选择的模型, 有改变模型大小的选择对象
    for(let i =0, length = this.resize_models_stack.length; i < length; i ++) {
        let model = this.resize_models_stack[i];
        ctx.strokeStyle = 'blue';
        ctx.strokeRect(model.x - 5, model.y - 5, model.width + 10, model.height + 10);
    }

    // 绘制区域选择
    if (this.area_selection_stack.length ===2) {
        let a = this.area_selection_stack[0];
        let b = this.area_selection_stack[1];
        let min_x = Math.min(a.offsetX, b.offsetX);
        let max_x = Math.max(a.offsetX, b.offsetX);
        let min_y = Math.min(a.offsetY, b.offsetY);
        let max_y = Math.max(a.offsetY, b.offsetY);

        ctx.strokeStyle = '#ff14f3';
        ctx.lineWidth = 1;
        ctx.setLineDash([5, 5]);
        ctx.strokeRect(min_x, min_y, max_x - min_x, max_y - min_y);
    }

    ctx.restore();
};


/**
 * 更新绘制的内容到画板
 * */
JEditor.prototype.update = function () {
    this.painter.begin();
    this.painter.render();
    this.painter.update();
};


/**
 * 在当前的模型列表终新建一个模型
 * */
JEditor.prototype.create_link = function (begin, end, profile) {
    let linked = this.painter.is_linked(begin, end);
    if ( linked ) {
        console.warn("锚点已经有过连接!");
        return undefined;
    }

    if ( begin === end ) {
        console.warn("不允许锚点连接自身！");
        return undefined;
    }

    if ( typeof begin != 'object' ) {
        let target = this.painter.search_anchor(begin);
        if ( ! target ) {
            console.error("没有找到锚点", begin);
            return undefined;
        }
        begin = target;
    }
    if ( typeof end != 'object' ) {
        let target = this.painter.search_anchor(end);
        if ( ! target ) {
            console.error("没有找到锚点", end);
            return undefined;
        }
        end = target;
    }

    if ( begin.model === end.model ) {
        console.warn("不允许模型自身的锚点连接！");
        return;
    }

    let id = ++ this.painter._id_pool;
    let link = new JLink(id, begin, end, profile);
    this.painter.links_list[id] = link;

    this.notify_link(link, begin, end);

    return link;
};

/**
 * 在当前的模型列表终新建一个模型
 * */
JEditor.prototype.create_anchor = function (model, profile) {
    let id = ++ this.painter._id_pool;
    if ( typeof model != 'object' ) {
        let target = this.painter.search_model(model);
        if ( ! target ) {
            console.error("没有找到模型", model);
            return undefined;
        }
        model = target;
    }
    let anchor = new JAnchor(id, model, profile);
    this.painter.anchors_list[id] = anchor;
    return anchor;
};

/**
 * 在当前的模型列表终新建一个模型
 * */
JEditor.prototype.create_model = function(profile) {
    let id = ++ this.painter._id_pool;

    profile.name = "model_" + id;

    let model = new JModel(id, this.painter, profile);
    this.painter.models_list[id] = model;
    return model;
};

/**
 * 将画板中的对象保存起来
 * */
JEditor.prototype.save = function () {
    let models = {};
    let links = {};
    let anchors = {};
    let libraries = {};

    for (let i in this.painter.image_libraries_list) {
        if ( ! this.painter.image_libraries_list.hasOwnProperty(i) ) {
            continue;
        }

        let pack = this.painter.image_libraries_list[i].save();
        libraries[pack.id] = pack;
    }

    for (let i in this.painter.links_list) {
        if ( ! this.painter.links_list.hasOwnProperty(i) ) {
            continue;
        }
        let pack = this.painter.links_list[i].save();
        links[pack.id] = pack;
    }

    for (let i in this.painter.anchors_list) {
        if ( ! this.painter.anchors_list.hasOwnProperty(i) ) {
            continue;
        }
        let pack = this.painter.anchors_list[i].save();
        anchors[pack.id] = pack;
    }

    for (let i in this.painter.models_list) {
        if ( ! this.painter.models_list.hasOwnProperty(i) ) {
            continue;
        }
        let pack = this.painter.models_list[i].save();
        models[pack.id] = pack;
    }

    return {
        models: models,
        links: links,
        anchors: anchors,
        libraries: libraries,
        id: this.painter.id,
        name: this.painter.name,
        background_color: this.painter.background_color,
        width: this.painter.width,
        height: this.painter.height
    };
};

/**
 * 从json对象加载到画板
 * */
JEditor.prototype.load = function (obj) {
    this.painter.load(obj.width, obj.height, obj.models, obj.anchors, obj.links, obj.libraries);
};


/**
 * 判断光标是否在改变大小的区域
 * */
JEditor.prototype.is_cursor_in_model_resize_area = function(model, ev) {
    if ( model.x > ev.offsetX ) {
        return false;
    }
    if ( model.x + model.width < ev.offsetX ) {
        return false;
    }
    if ( model.y > ev.offsetY ) {
        return false;
    }
    if ( model.y + model.height < ev.offsetY ) {
        return false;
    }

    return ev.offsetX > model.x_offset && ev.offsetY > model.y_offset;
};

/**
 * 判断光标是否在改变位置的区域内
 * */
JEditor.prototype.is_cursor_in_model_change_location_area = function(model, ev) {
    if ( model.x > ev.offsetX ) {
        return false;
    }
    if ( model.x + model.width < ev.offsetX ) {
        return false;
    }
    if ( model.y > ev.offsetY ) {
        return false;
    }
    if ( model.y + model.height < ev.offsetY ) {
        return false;
    }

    return !(ev.offsetX > model.x_offset && ev.offsetY > model.y_offset);
};


/**
 * 选择模型
 * */
JEditor.prototype.select_model = function (ev) {
    return this.painter.select_model(ev);
};


/**
 * 选择锚点
 * */
JEditor.prototype.select_anchor = function (ev) {
    return this.painter.select_anchor(ev);
};


/**
 * 选择连接线
 * */
JEditor.prototype.select_link = function (ev) {
    return this.painter.select_link(ev);
};


/**
 * 更新模型的位置
 **/
JEditor.prototype.update_model_location = function(model, new_x_offset, new_y_offset) {
    model.x_offset = new_x_offset;
    model.y_offset = new_y_offset;
    model.x = model.x_offset - model.width/2;
    model.y = model.y_offset - model.height/2;

    for (let name in model.anchors) {
        if ( model.anchors.hasOwnProperty(name) ) {
            let anchor = model.anchors[name];
            anchor.x = anchor.model.x_offset + anchor.x_offset - anchor.width / 2;
            anchor.y = anchor.model.y_offset + anchor.y_offset - anchor.height / 2;
        }
    }
};


/**
 * 更新模型的大小
 **/
JEditor.prototype.update_model_size = function(model, new_width, new_height) {
    model.width = new_width;
    model.height = new_height;

    // 固定中心点不变
    model.x = model.x_offset - model.width/2;
    model.y = model.y_offset - model.height/2;

    function relocation_anchor(model, anchor, x_offset, y_offset) {
        anchor.x_offset = x_offset;
        anchor.y_offset = y_offset;
        anchor.x = model.x_offset + anchor.x_offset - anchor.width/2;
        anchor.y = model.y_offset + anchor.y_offset - anchor.height/2;
    }

    // left anchor
    let anchor = model.anchors['E'];
    anchor && relocation_anchor(model, anchor, - new_width / 2, 0);

    // top anchor
    anchor = model.anchors['N'];
    anchor && relocation_anchor(model, anchor, 0, - new_height / 2);

    // right anchor
    anchor = model.anchors['W'];
    anchor && relocation_anchor(model, anchor, new_width / 2, 0);

    // bottom anchor
    anchor = model.anchors['S'];
    anchor && relocation_anchor(model, anchor, 0, new_height / 2);
};


/***
 *
 * 鼠标移动事件
 */
JEditor.prototype.onmousemove = function (ev) {
    let update_request = 0;

    /*
    let link = this.select_link(ev);
    if (link) {
        console.log(link);
    }*/

    // 跟踪热锚点位置, 光标移动至锚点上时用不同颜色的框描出边框
    let anchor = this.select_anchor(ev);
    if ( anchor && this.hot_anchors_stack.indexOf(anchor) < 0 ) {
        this.hot_anchors_stack.push(anchor);
        update_request ++;
    } else {
        this.hot_anchors_stack = [];
    }

    // 跟踪热线位置，随着光标的移动动态的绘制出连接线的位置
    if ( this.anchor_stack_selected.length > 0) {
        for (let idx in this.hotlines_stack) {
            if (!this.hotlines_stack.hasOwnProperty(idx)) {
                continue;
            }
            let hot_line = this.hotlines_stack[idx];
            hot_line.update_endpoint(ev.offsetX, ev.offsetY);
            update_request ++;
        }
    }

    let delta_x = 0, delta_y = 0;
    if ( this.cursor_motion_stack.length ) {
        delta_x = ev.offsetX - this.cursor_motion_stack[0].offsetX;
        delta_y = ev.offsetY - this.cursor_motion_stack[0].offsetY;
    }

    // 有位置变化时才进行更新操作，避免多次绘制
    if (delta_x || delta_y) {
        // 有改变模型位置的选择对象
        if (this.change_location_models_statck.length) {
            this.painter.dom.style.cursor = 'move';

            for(let i = 0, length = this.change_location_models_statck.length; i < length; i ++) {
                let model = this.change_location_models_statck[i];
                let attribute = this.attribute_of_selected_model_statck[model.id];

                let new_x_offset = attribute.x_offset + delta_x;
                let new_y_offset = attribute.y_offset + delta_y;
                this.update_model_location(model, new_x_offset, new_y_offset);
                update_request ++;
            }
        }
    }

    // 有位置变化时才进行更新操作，避免多次绘制
    if (delta_x || delta_y) {
        // 有改变模型大小的选择对象
        if (this.resize_models_stack.length) {
            this.painter.dom.style.cursor = 'nw-resize';

            for(let i =0, length = this.resize_models_stack.length; i < length; i ++) {
                let model = this.resize_models_stack[i];
                let attribute = this.attribute_of_selected_model_statck[model.id];
                let new_width = attribute.width + delta_x;
                if (new_width <= 20) {
                    new_width = 20;
                }
                let new_height = attribute.height + delta_y;
                if (new_height <= 20) {
                    new_height = 20;
                }
                this.update_model_size(model, new_width, new_height);
                update_request ++;
            }
        }
    }

    if ( update_request){
        console.log(update_request);
    }

    this.painter.onmousemove(ev);

    // 整体重绘一次，提高效率
    return update_request ? this.update() : undefined;
};

/**
 * 连接热线对象
 * */
let JHotline = function(begin_x, begin_y) {
    this.begin_x = begin_x;
    this.begin_y = begin_y;
    this.end_x = begin_x;
    this.end_y = begin_y;
};
JHotline.prototype.update_endpoint = function(end_x, end_y) {
    this.end_x = end_x;
    this.end_y = end_y;
};


/***
 *
 * 鼠标按下事件
 */
JEditor.prototype.onmousedown = function (ev) {
    this.painter.onmousedown(ev);

    let anchor = this.select_anchor(ev);

    // 只允许将锚点压栈一次
    if ( anchor && this.anchor_stack_selected.indexOf(anchor) < 0 ) {
        this.anchor_stack_selected.push(anchor);
        let hot_line = new JHotline(ev.offsetX, ev.offsetY);
        this.hotlines_stack.push(hot_line);
        return;
    }

    // 编辑模式下梳鼠标按下后应该优先选择锚点，然后选择模型
    let model = this.select_model(ev);
    if ( !model ) return;

    let attribute = {
        x_offset: model.x_offset,
        y_offset: model.y_offset,
        width: model.width,
        height: model.height
    };

    if (this.is_cursor_in_model_change_location_area(model, ev)) {
        if ( this.change_location_models_statck.indexOf(model) < 0 ) {
            this.change_location_models_statck.push(model);
        }
    } else { //if (this.is_cursor_in_model_resize_area(model, ev) ) {
        if ( this.resize_models_stack.indexOf(model) < 0 ) {
            this.resize_models_stack.push(model);
        }
    }

    this.attribute_of_selected_model_statck[model.id] = attribute;
    this.cursor_motion_stack.push(ev);
};

/***
 *
 * 鼠标弹起事件
 */
JEditor.prototype.onmouseup = function (ev) {
    let anchor = this.select_anchor(ev);

    if ( anchor && this.anchor_stack_selected.indexOf(anchor) < 0 ) {
        let begin_anchor = this.anchor_stack_selected.pop();

        // 切换连接的锚点
        if (anchor.model === begin_anchor.model) {
            let link = this.painter.search_link_by_anchor_object(begin_anchor);
            if (link) {
                console.log("change link", begin_anchor, anchor);
                if (link.begin === begin_anchor) {
                    link.begin = anchor;
                } else {
                    link.end = anchor;
                }
            } else {
                console.error("something is wrong!");
            }
        } else {
            // 现在已经有两个锚点了，判断一下：若还没有建立过连接，则新建一个连接
            let link = this.create_link(begin_anchor, anchor, {});
            console.log("new link:", link);
        }
    }

    let model = this.select_model(ev);

    if ( this.model_selected !== undefined ) {
        this.update();
    }

    this.painter.dom.style.cursor = 'auto';
    this.model_selected = undefined;
    this.move_begin_point = undefined;

    // 清空锚点选择栈,左键按下时选择,左键弹起时清空
    this.anchor_stack_selected = [];
    // 动态显示的锚点, 光标移动到锚点上时可以高亮显示，光标移入范围选择，移出范围清空
    this.hot_anchors_stack = [];
    // 跟随光标移动的线，选择锚点时激活，光标移动时更新，左键弹起时清空
    this.hotlines_stack = [];
    // 改变大小的对象选择栈，左键点击对象的第四象限时选择，光标移动时更新，左键弹起时清空
    this.resize_models_stack = [];
    // 改变位置的对象选择栈，左键点击对象的第一、二、三象限时选择，光标移动时更新，左键弹起时清空
    this.change_location_models_statck = [];
    // 选择的模型基本属性栈，选择时压入，左键弹起时清空
    this.attribute_of_selected_model_statck = {};
    // 光标移动的位置记录, 左键按下压栈两次，光标移动时更新最后一个，左键弹起时清空
    this.cursor_motion_stack = [];

    return this.painter.onmouseup(ev);
};

/**
 * 初始化jmodels编辑器
 * */
function initialize_jmodels_editor(painter) {
    let editor = new JEditor(painter);

    // 左键点击任意空白区域后，选择区的所有对象都会被清空
    painter.empty_event_listener.onmousedown(function (ev, painter) {
        editor.select_stack.empty();
        editor.area_selection_stack = [ev];
        console.log("select empty.");
    });
    // 无对象的左键弹起事件
    painter.const_event_listener.onmouseup(function (ev, painter) {
        // 有选择范围的情况下，将框选范围内的节点加入选中区域
        if (editor.area_selection_stack.length === 2) {
            let a = editor.area_selection_stack[0];
            let b = editor.area_selection_stack[1];

            let min_x = Math.min(a.offsetX, b.offsetX);
            let max_x = Math.max(a.offsetX, b.offsetX);
            let min_y = Math.min(a.offsetY, b.offsetY);
            let max_y = Math.max(a.offsetY, b.offsetY);

            let select_model_count = 0;
            for (let id in painter.models_list) {
                if (painter.models_list.hasOwnProperty(id)) {
                    let model = painter.models_list[id];
                    if (model.x_offset < min_x || model.x_offset > max_x) {
                        continue;
                    }
                    if (model.y_offset < min_y || model.y_offset > max_y) {
                        continue;
                    }
                    editor.select_stack.models.push(model);
                    select_model_count ++;
                }
            }
            if (select_model_count) {
                editor.update();
            }
        }

        editor.area_selection_stack = [];
    });
    // 无对象的光标移动事件
    painter.const_event_listener.onmousemove(function (ev, painter) {
        console.log("const mouse move.");
        if (ev.buttons && editor.area_selection_stack.length) {
            editor.area_selection_stack[1] = ev;
            editor.update();
        }
    });

    // 在节点上检测到光标移动事件
    painter.model_event_listener.onmousedown(function (ev, model) {
        if (editor.select_stack.models.indexOf(model) === -1) {
            // 判定shift键用于多选
            if (!ev.shiftKey) {
                editor.select_stack.models = [model]
            } else {
                editor.select_stack.models.push(model);
            }
            console.log("select model", model, ev);
        }
    });

    // 在节点上检测到了光标移动
    painter.model_event_listener.onmousemove(function (ev, model) {
        // 左键按下
        if (ev.buttons) {
            if (editor.select_stack.models.length)
            console.log("model mouse move", model, ev);
        }
    });

    // 在锚点上检测到光标移动
    painter.anchor_event_listener.onmousemove(function (ev, anchor) {
        //console.log("在锚点上检测到光标移动", anchor);
    });

    // 在连接线上检测到鼠标单击
    painter.link_event_listener.onclick(function (ev, link) {
        console.log("在连接线上检测到鼠标单击", link);
        if (editor.select_stack.links.indexOf(link) === -1) {
            // 判定shift键用于多选
            if (!ev.shiftKey) {
                editor.select_stack.links = [link]
            } else {
                editor.select_stack.links.push(link);
            }
            console.log("select link", link, ev);
        }
    });
    // 在连接线上检测到鼠标双击
    painter.link_event_listener.ondblclick(function (ev, link) {
        console.log("在连接线上检测到鼠标双击", link);
    });

    return editor;
}
