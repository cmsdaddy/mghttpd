/**
 * */


/*********************************************节点-对象*********************************************************
 * 节点对象
 * pid = 0, 表示是painter(root), 否则位jNode
 * */
let jNode = function (pid, id, profile) {
    this.profile = profile;

    this.pid = pid;
    this.id = id;

    this.location = new jLocation(profile.x, profile.y);
    this.size = new jSize(profile.width, profile.height);
};


/**
 * 根据提供的新的ID值，克隆一个新的节点对象
 * */
jNode.prototype.clone = function (id) {
};


/**
 * 根据提供的上下文，绘制这个节点
 * */
jNode.prototype.render = function (ctx) {
};


/*********************************************连接点-对象*********************************************************
 * 连接点对象
 * */
let jConnector = function(id, node, profile) {
    this.id = id;
    this.node = node;

    this.location = new jLocation(profile.x, profile.y);
    this.size = new jSize(profile.width, profile.height);
};
jConnector.prototype.links_list = function() {
};


/**********************************************连接-对象*********************************************************
 * 连接对象
 * */
let jLink = function(id, begin, end, profile) {
    this.profile = profile;
    this.id = id;

    this.begin = begin;
    this.end = end;
};
jLink.prototype.render = function(ctx) {
};


/**********************************************节点-变量*********************************************************
 * 变量节点，用于根据值不同而显示不同内容的需求
 * */
let jValueNode = function (id, profile) {
    this.name = profile.name;
};
jValueNode.prototype.render = function (ctx) {
};

