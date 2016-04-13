(function($) {
    $(document).ready(function() {
        var jobStatus = $("#job-status");

        if (jobStatus.length > 0) {
            var statusUrl = jobStatus.data('job-status-url'),
                progressBar = $("#progress-bar");
            if (statusUrl.length > 0) {
                var timerId = setInterval(function() {
                    $.ajax({
                        type: "GET",
                        url: statusUrl,
                        dataType: 'json',
                        success: function(data, textStatus, jqXHR) {
                            if (data.hasOwnProperty('progress')) {
                                if (data.progress > 0) {
                                    progressBar.val(data.progress);
                                }
                            }
                            if (data.hasOwnProperty('status')) {
                                if (data.status === 'FINISHED' || data.status === 'FAILED') {
                                    clearInterval(timerId);
                                    location.reload();
                                }
                            }
                        },
                        error: function(jqXHR, textStatus, errorThrown) {
                            clearInterval(timerId);
                            location.reload();
                        }
                    });
                }, 750);
            }
        }
    });
})(django.jQuery);
