define(['jquery'], function($) {
    return {
        init: function(performanceHtml) {
            $(document).ready(function() {
                $('.course-content').prepend(performanceHtml);
            });
        }
    };
});