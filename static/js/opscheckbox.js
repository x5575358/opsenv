	function swapCheck(value) {
		if (value) {
			$("input[type=checkbox]").each(function(){
					// $(item).removeProp('checked');
					// $(item).prop("checked", true);
					// console.log("----true--------");
			$.uniform.update($(this).prop("checked",true))
			})
		} else {
			$("input[type=checkbox]").each(function() {
				$.uniform.update($(this).prop("checked",false))
			});
		}
	}

	function releaseCheck(){
		var list = []
	    var url_head = document.getElementById("opscheckbox").getAttribute('value')
        $('.list-checkbox').each(function(index, item) {
        	if($(this).prop('checked')) {
            	list.push($(this).val())
                }
            })
        if (list.length != 0){
           let url=`${url_head}?exce_id=${JSON.stringify(list)}`
           console.log(url)
                //console.log("11111111")
           location.href=url
          }
   	}

    function releaseCheckPost(){
    	var list = []
        var url_head = document.getElementById("opscheckboxpost").getAttribute('value')
        $('.list-checkbox').each(function(index, item) {
        	if($(this).prop('checked')) {
            	list.push($(this).val())
            }
         })
         if (list.length != 0){
         	$.ajax({
            	url: `${url_head}`,
               	data: { 'exce_id':`${JSON.stringify(list)}`},
                type: "post",
                dataType: 'json',
                success: function(res){
                            location.href=res.data
                             }
                })
			}
		}

	//crete a function to commit post request
	function GetByIdpostRequest(){
		var post_handler = document.getElementById("postid");
		var url_head = post_handler.getAttribute('url_head');
		var exce_id  = post_handler.getAttribute('exce_id');
    	var list = []
		list.push(exce_id)
        $.ajax({
			url : `${url_head}`,	
			data: { 'exce_id':`${JSON.stringify(list)}`},
			type: "post",
			dataType: 'json',
			success: function(res){
            	location.href=res.data
           }
		})
	}
