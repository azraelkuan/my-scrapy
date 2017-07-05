/**
 * Created by Azrael on 2017/2/18.
 */
var key = "604128e90f0f7ca695c811e7ccf5d6f0"
function getprovince() {
    var url = "http://restapi.amap.com/v3/config/district?keywords=&subdistrict=1&showbiz=false&extensions=base&key=" + key;
    $.get(url, function (data, status) {
        var pros = data['districts']['0']['districts'];
        var pro_node = $("#province");
        pro_node.append("<option></option>");
        for(var i=0;i<pros.length;i++) {
            var pro_html = "";
            pro_html = "<option>" + pros[i]['name'] + "</option>";
            pro_node.append(pro_html);
        }

    });
}

function getcity(pro_name) {
    var url = "http://restapi.amap.com/v3/config/district?keywords="+ pro_name +"&subdistrict=1&showbiz=false&extensions=base&key=" + key;
    $.get(url, function (data, status) {
        var citys = data['districts']['0']['districts'];
        var city_node = $("#city");
        city_node.empty();
        city_node.append("<option></option>");
        for(var i=0;i<citys.length;i++) {
            var city_html = "";
            city_html = "<option>" + citys[i]['name'] + "</option>";
            city_node.append(city_html);
        }

    });
}

$("#settable").click(function () {
    var tablename = $("#tablename").val();
    if (tablename == "") {
        alert("表名不能为空");
    } else {
        var get_data = {table_name:tablename};
        var url = "http://127.0.0.1:5000/gaode/create_table";
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
    var tag = $("#tag").val();
    var keyword = $("#keyword").val();
    var tablename = window.table_name;
    if (city == "" && province == "") {
        alert("city or pro can't be null");
    } else if (tag == "" && keyword == "") {
        alert("tag and keyword, u need choose one");
    } else {
        var url = "http://127.0.0.1:5000/gaode/get_params";
        var post_data = {
            city: city,
            province: province,
            tag: tag,
            keyword: keyword,
            table_name: tablename
        };
        $.post(url, post_data, function (data, status) {
            var receive = JSON.parse(data);
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
    var get_data = {project:"gaode"};
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

function canceljob(e) {
    var url = "http://localhost:6800/cancel.json";
    var id_node = $(e).parent().parent().children()[1];
    var job_id = $(id_node).html();
    var get_data = {
        job:job_id,
        project:"gaode"
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

$("#getstate").click(function () {
    getjob();
});

$("#province").change(function () {
    var proname = $(this).val();
    getcity(proname);
});


function gettable() {
    var url = "http://127.0.0.1:5000/gaode/get_table";
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
    var url = "http://127.0.0.1:5000/gaode/export_table";
    window.open(url + "?table_name=" + table_name);
}

$("#tag-sp").click(function () {
    var tag_node = $("#tag");
    tag_node.val("");
    tag_node.val("060200;060201;060202;060400;060401;060402;060403;060404;060405;060406;060407;060408;060409;060411;060413;060414;060415;060100;060102;060103;060101");

});

$("#tag-cosmetic").click(function () {
    var tag_node = $("#tag");
    tag_node.val("");
    tag_node.val("061400;061401;060411");

});

gettable();
getprovince();
getjob();

