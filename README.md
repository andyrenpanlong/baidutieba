
#分布式爬虫-----百度贴吧的数据抓取

目前程序只要分两部分跑，getAllList主要负责获取要爬取得所有的链接，分两部分存储，一份放在mongodb中，作为备份，另外一部分存在redis中，主要靠redis来支持分布式网络爬虫的信息分发； redis这部分放在主服务中，也是分布式服务器的master节点，也就是主服务器执行这段代码就可以了；

tiebaspider负责信息的抓取和数据的收集，也是存储在mongodb中，这部分抓取的主要内容为楼层回复和用户等相关信息；

##表结构及其说明：
TieBaList:   //所有的帖子链接
    {
    "id":4551008986,    //帖子的id
    "author_name":"rang叮咚",  //用户名（笔名）
    "first_post_id":89779054227,   //贴吧id
    "reply_num":0,  //回复数量
    "is_bakan":null, //吧务
    "vid":"",
    "is_good":null, //是否是商品类
    "is_top":null,  //是否是置顶帖
    "is_protal":null,
    "is_membertop":null,    //是否成员置顶
    "is_multi_forum":null,  //是否多论坛
    "frs_tpoint":null
}
    
Content： //帖子内容  
{
    "author":{
        "user_id":2257334880,  //用户id
        "user_name":"rang叮咚",   // 用户名
        "name_u":"%E7%B4%AB%E6%9E%81%E6%98%9F%E4%B8%BB&ie=utf-8",
        "user_sex":0,   //用户性别
        "portrait":"fb21e7b4abe69e81e6989fe4b8bb83b2", //用户头像
        "is_like":0,
        "level_id":1,   //等级id
        "level_name":"初涉江湖",    //等级名称
        "cur_score":0,
        "bawu":0,   //吧务
        "props":null，
    },
    "content":{
        "post_id":89779054227,  //帖吧id
        "is_anonym":false, //是否真名
        "forum_id":1998462,  //论坛id
        "thread_id":4551008986,  //贴子id
        "content":"　　根据最新公开信息，乐视超级电视这次对语音交互系统进行了升级，创造性推出多个智能化的语音交互服务，其中最让人脑洞大开的是语音弹幕功能。具体实现方式，是将乐视超级摇控器第三代与电视进行配对，成功后，用户只要说出“打开弹幕”、“我要吐槽”等关键词就能进入语音弹幕模式，系统将自动把用户说出的话转换成文字，然后在电视中显示出来，分享给收看同一视频资源(如赛事直播、热门影视剧等)的广大观众。对于乐视超级电视的新用户来说，可在电视到家后第一时间率先体验语音弹幕功能。而对于老用户而言，只需要购买一个超级摇控器第三代，就可以免除了手工打字的麻烦，同时也不会因为发送弹幕而错过了精彩的视频内容，更重要的是，还能为后续体验更多的超级电视创新功能做好准备!",
        "post_no":1,      //发帖数量
        "type":"0", //帖子的类型
        "comment_num":0,    //评论的数量
        "props":null,
        "post_index":0,  //帖子所在楼层
        "pb_tpoint":null,
        "open_id":"tbclient",  //
        "open_type":"android",  //打开的设备
        "date":"2017-08-07 02:26",  //创建时间
        "vote_crypt":"",
        "ptype":"0",
        "is_saveface":false
    }
}
