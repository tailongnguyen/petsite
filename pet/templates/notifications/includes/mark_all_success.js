var markAllSuccess = function (response) {
    //console.log(response);
    // console.log(response.action);
    var action = 'read';

    if (response.action == 'read') {
        var mkClass = readNotificationClass;
        var rmClass = unreadNotificationClass;
    } else {
        mkClass = unreadNotificationClass;
        rmClass = readNotificationClass;
    }
    // console.log(mkClass);
    // console.log(rmClass);
    var notification = $(nfSelector);
    notification.removeClass('read').addClass('unread');
    var btn = $(markNotificationSelector);

    btn.html('unread');
};
