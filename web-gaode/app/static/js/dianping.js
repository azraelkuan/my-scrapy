/**
 * Created by Azrael on 2017/3/28.
 */

$("#settable").click(function () {
    var tablename = $("#tablename").val();
    if (tablename == "") {
        alert("表名不能为空");
    } else {
        var get_data = {table_name:tablename};
        var url = "http://127.0.0.1:5000/dianping/create_table";
        $.get(url, get_data, function (data, status) {
            var receive = JSON.parse(data);
            if (receive['status']) {
                alert("create failed, please change the table name");
            } else {
                $("#settable").text("success");
                $("#settable").attr("class", "btn btn-success");
                $("#settable").attr("disabled",true);
                window.table_name = tablename;
            }
        })
    }
});


$("#submitall").click(function () {
    var city = $("#city").val();
    var province = $("#province").val();
    var cityid = $("#cityId").val();
    var catid = $("#catId").val();
    var tablename = window.table_name;
    if (city == "" || province == "") {
        alert("city or pro can't be null");
    } else  if(tablename == null) {
      alert("table_name is empty");
    } else if (cityid == "" || catid == "") {
        alert("cityid and catid all need");
    } else {
        var url = "http://127.0.0.1:5000/dianping/get_params";
        var post_data = {
            city: city,
            province: province,
            cityid: cityid,
            catid: catid,
            table_name: tablename
        };
        console.log(post_data);
        $.post(url, post_data, function (data, status) {
            var receive = JSON.parse(data);
            console.log(data);
            if (receive['status'] == 'ok') {
                $("#submitall").text("success to submit");
                $("#submitall").attr("class", "btn btn-success");
                $("#submitall").attr("disabled",true);
                window.jobid = receive['jobid'];
            } else {
                alert("failed to create a spider");
            }
        });
    }

});

function getjob() {
    var url = "http://localhost:6800/listjobs.json";
    var get_data = {project:"mdianping"};
    $.get(url, get_data, function (data, status) {
        var receive = data;
        if (receive['status'] == 'ok') {
            var tbody = $("#state tbody");
            var finished = "";
            $.each(receive['running'], function(index, value) {
                var tmp_node = "<tr>" +
                    "<td>" + "running" + "</td>" +
                    "<td>" + value['id'] + "</td>" +
                    "<td>" + value['start_time'] + "</td>" +
                     "<td>" + "<button class='btn btn-danger btn-sm' onclick='canceljob(this)'>cancel this job</button>"  +"</td>"
                    + "</tr>";
                finished += tmp_node;
            });
            tbody.html(finished);
        }
    })
}

$("#getstate").click(function () {
    getjob();
});

function canceljob(e) {
    var url = "http://localhost:6800/cancel.json";
    var id_node = $(e).parent().parent().children()[1];
    var job_id = $(id_node).html();
    var get_data = {
        job:job_id,
        project:"mdianping"
    };
    $.post(url, get_data, function (data, status) {
         var receive = data;
         if (receive['status'] == 'ok') {
             alert("sucess to cancel");
         } else {
             alert("fail to cancel");
         }
    });
}

getjob();


function gettable() {
    var url = "http://127.0.0.1:5000/dianping/get_table";
    $.get(url, function (data, status) {
        var receive = JSON.parse(data);
        var tbody = $("#table tbody");
        var table_html = "";
        $.each(receive, function(index, value) {
                var tmp = "<tr>" + "<td>" + value +
                    "</td>" + "<td>" + "<button class='btn btn-sm btn-primary' onclick='exporttable(this)'>export this table</button>" +
                    "</td>" +
                    "</tr>";
                table_html += tmp;
            });
        tbody.html(table_html);
    })
}

function exporttable(e) {
    var table_name_node = $(e).parent().parent().children()[0];
    var table_name = $(table_name_node).html();
    var url = "http://127.0.0.1:5000/dianping/export_table";
    window.open(url + "?table_name=" + table_name);
}

gettable();

