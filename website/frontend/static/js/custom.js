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
        var fileInputElement = $('#file-input');
        var files = fileInputElement.files

        var formData = new FormData();

        for (var i = 0; i < files.length; i++) {
            var file = files[i];

            // Check the file type.
            if (!file.type.match('text.*')) {
                continue;
            }

            // Add the file to the request.
            formData.append('files[]', file, file.name);
        }
        //formData.append("txtfiles", fileInputElement.files[0]);

// JavaScript file-like object
//        var content = '<a id="a"><b id="b">hey!</b></a>'; // the body of the new file...
//        var blob = new Blob([content], {type: "text/xml"});
//
//        formData.append("webmasterfile", blob);

        var request = new XMLHttpRequest();
        request.open("POST", "/classify/file");
        request.send(formData);
    });

//    onchange sentence-input
    $('#sentence-button').on('click', function (event) {

    });

//    onchange post-url-input
    $('#post-url-button').on('click', function (event) {

    });
});