$(document).ready(function(){
    $(".like").click(function(){

        var id = this.id;
        var split_id = id.split("_");
        var postid = split_id[1];
        var boardid = split_id[2];

        $.ajax({
            url: '/like-post/' + boardid,
            type: 'post',
            data: {postid:postid},
            dataType: 'json',
            success: function(data){
                var likes = data['post_likes'];
                var userliked = data['user_liked'];
                $("#likes_"+postid).text(" "+likes);
                $("#likes_"+postid).removeClass("fas fa-thumbs-up").addClass(userliked);
            }
        });
    });
});