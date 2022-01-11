$(document).ready(function() {
    const socket = io.connect('http://127.0.0.1:5000');

    $('.stats-card').hide();

    $('.handle-form').submit(function(event) {
        event.preventDefault();
        const handle = $('.input-handle').val();
        socket.emit('add_task', { 'handle': handle });
    });


    function drawStats(stats) {
        $('.solved-tasks').text(stats.handle);
        $('.unsolved-tasks').text(stats.handle);
    };

    function calcStats(submissions) {
        const statsResult = {
            solvedTasks: 0,
            solvedRatedTasks: 0,
            sumRating: 0,
            okCount: 0,
            waCount: 0,
            mlCount: 0,
            tlCount: 0
        }

        const solvedTasks = new Set()
        const tasksRating = new Map()

        for (const submission of submissions) {
            if (submission.verdict == "OK") {
                statsResult.okCount += 1;
                solvedTasks.add(submission.contest_id + "/" + submission.problem_index);
                if (submission.rating) {
                    tasksRating.set(submission.contest_id + "/" + submission.problem_index, submission.rating, +submission.rating);
                }
            }
            if (submission.verdict == "WRONG_ANSWER") {
                statsResult.waCount += 1;
            }
            if (submission.verdict == "TIME_LIMIT_EXCEEDED") {
                statsResult.tlCount += 1;
            }

            if (submission.verdict == "MEMORY_LIMIT_EXCEEDED") {
                statsResult.mlCount += 1
            }
        }

        statsResult.solvedTasks = solvedTasks.size;
        for (const [key, value] of tasksRating) {
            statsResult.sumRating += value;
            statsResult.solvedRatedTasks += 1;
        }

        return statsResult;
    };

    socket.on('draw_stats', function(data) {
        console.log(data);
        //drawStats(data);
        $('.stats-card').show();
    });


    socket.on('run_task', function(data) {
        //alert(data.msg)
        const submissions = jQuery.parseJSON(data);
        const statsResult = calcStats(submissions);

        alert(JSON.stringify(statsResult));
        //socket.emit()

    })

});