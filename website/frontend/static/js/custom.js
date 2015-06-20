// preloader
$(window).load(function () {
    $('.preloader').fadeOut(1000); // set duration in brackets    
});

$(function () {
    new WOW().init();
    $('.templatemo-nav').singlePageNav({
        offset: 70
    });

    /* Hide mobile menu after clicking on a link
     -----------------------------------------------*/
    $('.navbar-collapse a').click(function () {
        $(".navbar-collapse").collapse('hide');
    });

    /*
     * FACEBOOK SENTIMENT ANALYSIS
     * */

//    onchange file-input
    $('#file-button').on('click', function (event) {
        console.log("file_input");
    });

//    onchange sentence-input
    $('#sentence-button').on('click', function (event) {
        console.log("sentence_button");
    });

//    onchange post-url-input
    $('#post-url-button').on('click', function (event) {
        console.log("post_url_button");
    });
});