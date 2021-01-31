$('.my-menu-item').each(function() {
    $(this).on('click', function() {
        reset_link()
        $(this).addClass('g-color-secondary')
        //$(this).addClass('text-white')
        link = $(this).attr('id')
        GplFwk.ajax.getAjax(link, "main-div", "GET");
    });

})

var reset_link = function(){
    $('.my-menu-item').each(function() {
        $(this).removeClass('g-color-secondary')
        //$(this).addClass('text-gray-500')
    })
} 
/*
$('.menu-item2').each(function() {
    $(this).on('click', function() {
        //$(this).prop("style", "background-color: gray")
        //link_id = $(this).attr("id")
        $("#maindiv").html('<span></span>')
        link = $(this).attr('id')
        GplFwk.ajax.getAjax(link, "selectdiv", "GET");
    });
    
    if ($(this).attr("id") != link_id) {
        console.log($(this).attr("id"))
        $(this).prop("style", "")
    }
    
})
*/