/**
 * 位置对象
 * */
let jLocation = function (x, y) {
    this.x = x;
    this.y = y;
};


/**
 * 到另一个位置对象的距离
 * */
jLocation.prototype.distance = function(other) {
    let delta_x = this.x - other.x;
    let delta_y = this.y - other.y;

    return Math.sqrt(delta_x * delta_x + delta_y * delta_y);
};


/**
 * 根据自身数据克隆一个位置对象
 * */
jLocation.prototype.clone = function() {
    return new jLocation(this.x, this.y);
};


/**
 * 尺寸对象
 * */
let jSize = function (width, height) {
    this.width = width;
    this.height = height;
};
jSize.prototype.get_width = function () {
    return this.width;
};
jSize.prototype.get_height = function () {
    return this.height;
};
