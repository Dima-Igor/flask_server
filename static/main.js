$(document).ready(function() {
    const socket = io.connect('http://127.0.0.1:5000');

    $('.stats-card').hide();

    $('.handle-form').submit(function(event) {
        event.preventDefault();
        const handle = $('.input-handle').val();
        socket.send({ 'handle': handle });
    });


    function drawStats(stats) {
        $('.solved-tasks').text(stats.handle);
        $('.unsolved-tasks').text(stats.handle);
    };

    function calcStats(data) {

    };

    socket.on('draw_stats', function(data) {
        console.log(data);
        //drawStats(data);
        $('.stats-card').show();
    });


    socket.on('run_task', function(data) {
        alert(data);
    })

});