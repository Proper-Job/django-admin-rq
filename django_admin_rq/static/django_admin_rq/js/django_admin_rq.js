(function($) {
    $(document).ready(function() {
        var jobStatus = $("#job-status");

        if (jobStatus.length > 0) {
            var jobRunning = jobStatus.data('job-running'),
                statusUrl = jobStatus.data('job-status-url'),
                progressBar = $("#progress-bar"),
                timerId;
            if (jobRunning && statusUrl) {
                timerId = setInterval(function() {
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
                }, 500);
            }
        }
    });
})(django.jQuery);
