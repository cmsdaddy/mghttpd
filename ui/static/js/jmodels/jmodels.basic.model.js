/**
 * 模型对象
 * */
let JModel = function (id, painter, profile) {
    this.id = id;

    this.painter = painter;
    this.profile = profile;

    this.x_offset = profile.x_offset;
    this.y_offset = profile.y_offset;
    this.x = Math.round(this.x_offset - profile.width/2);
    this.y = Math.round(this.y_offset - profile.height/2);
    this.width = profile.width;
    this.height = profile.height;

    this.name = profile.name;
    this.showed = (profile.showed === true);
    this.show_boarder = (profile.show_boarder === true);
    this.title = profile.title ? profile.title : '';
    this.comment = profile.comment ? profile.comment : '';
    this.font_size = profile.font_size ? profile.font_size : 10;
    this.font_color = profile.font_color? profile.font_color: "#000000";
    this.init_value = profile.init_value ? profile.init_value : 'n/a';
    this.datasource = profile.datasource ? profile.datasource: '';
    this.href = profile.href ? profile.href: '';
    this.default_href = this.href;

    this.value = profile.init_value;
    this.vmap = profile.vmap ? profile.vmap : {};

    // 显示图片
    this.h_scale = 0;
    this.v_scale = 0;
    this.degree = 0;
    this.vm = null;
    this.image = null;

    // 所有的锚点都需要注册在这里
    this.anchors = {};

    // 绑定的事件函数
    // 尺寸变化回调
    this._onresize = [];
    this.onresize = function (callback) {this._onresize.push(callback); return this;};

    // 位置变化回调
    this._onrelocation = [];
    this.onrelocation = function (callback) {this._onrelocation.push(callback); return this;};

    // 新建一个鼠标事件监听器
    this.event_listener = new JEventListener(this);

    // 设置初始状态值
    this.set_value('n/a');
    return this;
};

/**
 * 设置当前节点的值
 * */
JModel.prototype.set_value = function(value) {
    for (let id in this.vmap) {
        if (this.vmap.hasOwnProperty(id)) {
            let vm = this.vmap[id];
            if (!vm.img) {
                continue;
            }

            if (vm.value == value || vm.value === '*') {
                this.vm = vm;
                this.h_scale = vm.h_scale;
                this.v_scale = vm.v_scale;
                this.degree = vm.degree;

                this.image = new Image();
                this.image.src = vm.img;
                break
            }
        }
    }
};

/**
 * 判断指定的鼠标事件的光标范围在这个模型范围内
 * */
JModel.prototype.is_cursor_in = function(ev) {
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

JModel.prototype.do_onmousemove_callback = function(ev) {
    let length = this._onmousemove.length;
    for ( let i = 0; i < length; i ++ ) {
        this._onmousemove[i](ev, this);
    }
};

/**
 * 渲染函数
 * */
JModel.prototype.render = function (ctx) {
    // 控制外框显示
    if ( this.show_boarder ) {
        ctx.strokeRect(this.x-0.5, this.y-0.5, this.width, this.height);
    }
    if (this.title && this.title.length) {
        ctx.fillStyle = this.font_color;
        ctx.fillText(this.title, this.x-0.5, this.y + this.height + 12);
    }

    if ( this.image && this.image.complete ) {
        ctx.save();
        // 将坐标转移到中心点上
        ctx.translate(this.x_offset, this.y_offset);

        if ( this.degree ) {
            // 旋转指定角度
            ctx.rotate(Math.PI * 2 * this.degree / 360);
        }

        let h_scale = 1,v_scale = 1;
        if ( this.h_scale ) {
            h_scale = this.h_scale;
        }
        if ( this.v_scale ) {
            v_scale = this.v_scale;
        }
        if ( h_scale + v_scale < 2 ) {
            ctx.scale(h_scale, v_scale);
        }

        ctx.drawImage(this.image, -this.width/2, -this.height/2, this.width, this.height);
        ctx.restore();
    }
};

/**
 * 生成保存锚点对象
 * */
JModel.prototype.save = function () {
    return {
        id: this.id,
        name: this.name,
        x_offset: Math.round(this.x_offset),
        y_offset: Math.round(Number(this.y_offset)),
        width: Math.round(this.width),
        height: Math.round(Number(this.height)),
        showed: this.showed,
        show_boarder: this.show_boarder,
        title: this.title,
        comment: this.comment,
        font_size: this.font_size,
        init_value: this.init_value,
        datasource: this.datasource,
        vmap: this.vmap,
        href: this.href,
    }
};

/**
 * 显示模型
 * */
JModel.prototype.hide = function () {
    this.showed = false;
};
JModel.prototype.hidden = JModel.prototype.hide;

JModel.prototype.show = function () {
    this.showed = true;
};

JModel.prototype.toggle = function () {
    this.showed = this.showed === false;
};

JModel.prototype.blink = function (hz) {
};