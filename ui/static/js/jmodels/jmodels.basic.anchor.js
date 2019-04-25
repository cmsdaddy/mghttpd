/**
 * 锚点对象，用于链接两个对象
 * @param id: 锚点ID
 * @param model: 所属模型
 * @param x_offset: 当前锚点在模型的中心点的x偏移值
 * @param y_offset: 当前锚点在模型的中心点的y偏移值
 * @param style: 当前锚点的风格定义结构
 * */
let JAnchor = function (id, model, profile) {
    this.id = id;
    this.model = model;

    model.anchors[profile.name] = this;

    this.name = profile.name;
    this.x_offset = profile.x_offset;
    this.y_offset = profile.y_offset;
    this.height = 6;
    this.width = 6;

    this.x = model.x_offset + this.x_offset - this.width/2;
    this.y = model.y_offset + this.y_offset - this.height/2;

    return this;
};


/**
 * 判断指定的鼠标事件的光标范围在这个锚点范围内
 * */
JAnchor.prototype.is_cursor_in = function(ev) {
    if ( this.x > ev.offsetX ) {
        return false;
    }
    if ( this.x + this.width < ev.offsetX ) {
        return false;
    }
    if ( this.y > ev.offsetY ) {
        return false;
    }

    if ( this.y + this.height < ev.offsetY ) {
        return false;
    }

    return true;
};

/**
 * 渲染函数
 * */
JAnchor.prototype.render = function (ctx) {
};


/**
 * 生成保存锚点对象
 * */
JAnchor.prototype.save = function () {
    return {
        id: this.id,
        model: this.model.id,
        name: this.name,
        x_offset: this.x_offset,
        y_offset: this.y_offset,
    }
};
