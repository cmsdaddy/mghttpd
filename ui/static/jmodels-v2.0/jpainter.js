let jDomMask = function(painter) {
    // 绘制位置的父节点
    this.parent = painter.master_dom.parentNode;

    // 创建一个字符绘制蒙版
    this.dom = document.createElement('div');
    this.dom.id = painter.canvas_dom_id + '_text';
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
jDomMask.prototype.update_text = function(id, text) {
    if (this.doms.hasOwnProperty(id)) {
        this.doms[id].innerText = text;
    }
};


// 在(x, y)位置处显示字符串text, 格式在css中定义
jDomMask.prototype.new_text = function(id, name, x, y, text, css) {
    let span = document.createElement('span');

    span.id = id;
    span.name = name;
    span.innerText = text;

    let span_style = "position: absolute;";
    span_style += "float: left;";
    span_style += "left: " + x + 'px;';
    span_style += "top: " + y + 'px;';

    for (let name in css) {
        if (css.hasOwnProperty(name)) {
            css_name = name.replace('_', '-');
            console.log(name);
            span_style += (css_name + ': ' + css[name] + ';');
        }
    }

    span.style.cssText = span_style;
    this.dom.appendChild(span);

    this.doms[id] = span;
};


jDomMask.prototype.new_edit_box = function(id, name, x, y, text, css) {
};


/**
 * 绘图管理对象
 * */
let jPainter = function(canvas_dom_id, profile) {
    this.profile = profile;

    this.size = new jSize(profile.width, profile.height);

    this.canvas_dom_id = canvas_dom_id;

    // 主显示面板
    this.master_dom = document.getElementById(canvas_dom_id);
    this.master_ctx = this.master_dom.getContext('2d');

    // 创建一个绘制面板，主要是为了避免刷新过程产生的闪烁
    let parent = this.master_dom.parentNode;

    this.slave_dom = document.createElement('canvas');
    parent.appendChild(this.slave_dom);

    this.slave_dom.id = this.canvas_dom_id + '_shadow';
    this.slave_dom.style.display = "none";
    this.slave_ctx = this.slave_dom.getContext('2d');

    // 设置绘制窗口的大小
    this.slave_ctx.canvas.width = this.master_ctx.canvas.width = this.size.get_width();
    this.slave_ctx.canvas.height = this.master_ctx.canvas.height = this.size.get_height();

    // 创建一个文本处理dom, 用于处理节点或其他要显示文本的情况
    this.dom_mask = new jDomMask(this);

    this.master_ctx.fillStyle = '#eeeeee';
    this.master_ctx.fillRect(0, 0, this.size.get_width(), this.size.get_height());

    this.funney_location = new jLocation(400, 400);
    this.offset = 5;

    this.master_ctx.fillStyle = 'red';
    this.master_ctx.arc(this.funney_location.x, this.funney_location.y, 50, 0, Math.PI*2, true);
    this.master_ctx.fill();

    this.dom_mask.new_text(1, 'text', 100, 100, "hello world!", {font_size: '30px;', border_left: "red solid 1px;", color: 'red'});
    this.dom_mask.new_text(2, 'text', 100, 200, "hello world!", {});
};


jPainter.prototype.render = function () {
};


jPainter.prototype.clear_rect = function(x, y, width, height) {
    if (x < 0) {
        x = 0;
    }
    if (y < 0) {
        y = 0;
    }
    this.master_ctx.fillStyle = 'rgba(255,255,255,0.3)';
    this.master_ctx.fillRect(x, y, width, height);
    this.master_ctx.fill();
};


jPainter.prototype.clear = function(){
};


jPainter.prototype.rend_for_fun = function () {
    this.clear_rect(0, 0, this.size.get_width(), this.size.get_height());

    this.funney_location.x += this.offset;
    if (this.funney_location.x > this.size.get_width() - 50) {
        this.offset = -5;
        this.funney_location.x = this.size.get_width() - 50;
    }

    if (this.funney_location.x < 50) {
        this.offset = 5;
        this.funney_location.x = 50;
    }

    this.dom_mask.update_text(1, [this.funney_location.x].join(' '));

    this.master_ctx.save();
    this.master_ctx.translate(this.funney_location.x, this.funney_location.y);
    this.master_ctx.beginPath();
    this.master_ctx.arc(0, 0, 50, 0, Math.PI*2, true);
    this.master_ctx.closePath();
    this.master_ctx.fillStyle = 'rgba(255,0,255)';
    this.master_ctx.fill();
    this.master_ctx.restore();

};

