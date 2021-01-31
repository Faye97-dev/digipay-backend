var GplFwk = GplFwk || {};
var style =
  "<style>.center { display: block;margin-left: auto; margin-right: auto; }</style>";
var spinner =
  style +
  "<img src='../static/img/spin.gif' border='0' class='spinner center'> ";
GplFwk.ajax = {
  getAjax: function (url_, resdom, httpMethod, dataToPost, csrftoken) {
    $.ajax({
      beforeSend: function (xhr) {
        if (url_.indexOf("printorder") == -1) {
          $("#" + resdom).html(spinner);
        }
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },
      url: url_,
      type: httpMethod,
      dataType: "html",
      data: dataToPost,
      success: function (res) {
        if (url_.indexOf("printorder") !== -1) {
          var pdfdoc = new jsPDF();
          pdfdoc.fromHTML();
          pdfdoc.fromHTML(res, 10, 10, {
            width: 110,
            elementHandlers: "",
          });
          pdfdoc.save("order.pdf");
        } else {
          $("#" + resdom).html(res);
        }
      },
      error: function (jqXHR, textStatus, errorThrown) {
        var err =
          "<div class='alert alert-danger'> " +
          jqXHR.responseText +
          "<br>" +
          textStatus +
          "<br>" +
          errorThrown +
          "</div>";
        $("#" + resdom).html(err);
      },
    });
  },
};

var ServiceBakend = ServiceBakend || {};

ServiceBakend.ajax = {
  SendData: function (url_, dataToPost, csrftoken, success, failed) {
    $.ajax({
      beforeSend: function (xhr) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      },

      url: url_,
      type: "POST",
      data: dataToPost,

      success: success,

      error: failed,
    });
  },
};
