// custom javascript

$( document ).ready(() => {
  console.log('Sanity Check!');
});

$('.btn').on('click', function() {
  $.ajax({
    url: '/object/images',
    data: { type: $(this).data('object') },
    method: 'GET'
  })
  .done((res) => {
    getStatus(res.task.id);
  })
  .fail((err) => {
    console.log(err);
  });
});

function getStatus(taskID) {
  $.ajax({
    url: `/tasks/${taskID}`,
    method: 'GET'
  })
  .done((res) => {
    const html = `
      <tr>
        <td>${res.task.id}</td>
        <td>${res.task.status}</td>
        <td>${res.task.enqueued}</td>
      </tr>`
    $('#tasks').prepend(html);
    const taskStatus = res.task.status;
    if (taskStatus === 'finished' || taskStatus === 'failed') return false;
    setTimeout(function() {
      getStatus(res.task.id);
    }, 1000);
  })
  .fail((err) => {
    console.log(err);
  });
}
