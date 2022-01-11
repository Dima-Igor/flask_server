$(document).ready(function() {
    const socket = io.connect('http://127.0.0.1:5000');

    $('.stats-card').hide();

    $('.handle-form').submit(function(event) {
        event.preventDefault();
        const handle = $('.input-handle').val();
        socket.emit('add_task', { 'handle': handle });
    });


    function drawStats(stats) {
        $('.solved-tasks').text(`Количество решенных задач: ${stats.solvedTasks}`);
        $('.solved-rated').text(`Количество решенных рейтинговых задач: ${stats.solvedRatedTasks}`);
        $('.average-rating').text(`Средний рейтинг решенных задач: ${stats.averageRating}`);
        $('.ok-count').text(`Количество посылок со статусом ОК: ${stats.okCount}`);
        $('.wa-count').text(`Количество посылок со статусом Wrong answer: ${stats.waCount}`);
        $('.ml-count').text(`Количество посылок со статусом Memory limit: ${stats.mlCount}`);
        $('.tl-count').text(`Количество посылок со статусом Time limit: ${stats.tlCount}`);

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
        const stats = jQuery.parseJSON(data);
        drawStats(stats);
        $('.stats-card').show();
    });


    socket.on('run_task', function(data) {
        const submissions = jQuery.parseJSON(data);
        const statsResult = calcStats(submissions);

        socket.emit('get_task_result', {
            'solvedTasks': statsResult.solvedTasks,
            'solvedRatedTasks': stats.solvedRatedTasks,
            'sumRating': stats.sumRating,
            'okCount': stats.okCount,
            'waCount': stats.waCount,
            'mlCount': stats.mlCount,
            'tlCount': stats.tlCount
        });
    })

});