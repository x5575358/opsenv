var UIModals = function () {

    
    var initModals = function () {
       
       	$.fn.modalmanager.defaults.resize = true;
		$.fn.modalmanager.defaults.spinner = '<div class="loading-spinner fade" style="width: 200px; margin-left: -100px;"><img src="/static/image/fancybox_loading.gif" align="middle">&nbsp;<span style="font-weight:300; color: #eee; font-size: 18px; font-family:Open Sans;">&nbsp;Loading...</div>';


       	var $modal = $('#ajax-modal');
 
		$('#modal_ajax_demo_btn').on('click', function(){
		  // create the backdrop and wait for next modal to be triggered
		  $('body').modalmanager('loading');
		 
		  setTimeout(function(){
		     $modal.load('ui_modals_ajax_sample.html', '', function(){
		      $modal.modal();
		    });
		  }, 1000);
		});

		//get_difference_container get docker info js
		$('#modal_ajax_get_dockerinfo_btn').on('click', function(){
		    var src_obj = document.getElementById("src_opt")
		    var dest_obj = document.getElementById("dest_opst")
			var index = src_obj.selectedIndex;//获取选中的第一个id
			var dest_index = dest_obj.selectedIndex;//获取选中的第一个id
		    var src_value = src_obj.options[index].value;//获取选中id对应的值
		    var dest_value = dest_obj.options[dest_index].value;
            var error_obj = document.getElementById("error_hint")
		    console.log("---------ednd--------")
            error_obj.style.display= "none"
           if(src_value==null||src_value==""||dest_value==null||dest_value==""||src_value==dest_value){
                 error_obj.style.display="block"
                error_obj.innerHTML="源环境组和目的环境组不能一样，或者不能为空，请重新输入!"
				return
			}

        var url_head = error_obj.getAttribute('hear_url')
        console.log("-------2------")
        $.ajax({
           url: `${url_head}`,
           data: { 'src_name':`${JSON.stringify(src_value)}`, 'dest_name':`${JSON.stringify(dest_value)}`},
           type: "post",
           dataType: 'json',
           success: function(res){
                 console.log("res-----")
                 console.log("res--url_dest---",res.data)
//                 location.href=res.data
                 location.reload()
                 }
           })

         //release version
//         $('#modal_ajax_release_btn').on('click', function(){
//			var name = document.getElementById("exce_name_hint").value;
  //          console.log("4444444444")
   //      console.log(name)
            

//		}
       
          $('body').modalmanager('loading');

          setTimeout(function(){
             $modal.load('ui_modals_ajax_sample.html', '', function(){
              $modal.modal();
            });
          }, 1000);
        });

		$('#modal_ajax_release_btn').on('click', function(){
			var hint_obj = document.getElementById("exce_name_hint");
       		var name = hint_obj.getAttribute('value');
            var url_head = hint_obj.getAttribute('hear_url');
			let url=`${url_head}?exce_name=${JSON.stringify(name)}`
			console.log("4444444444",url_head)
			console.log(name)
			location.href=url
			$('body').modalmanager('loading');

          setTimeout(function(){
             $modal.load('ui_modals_ajax_sample.html', '', function(){
              $modal.modal();
            });
          }, 1000);
        });

		 
		$modal.on('click', '.update', function(){
		  $modal.modal('loading');
		  setTimeout(function(){
		    $modal
		      .modal('loading')
		      .find('.modal-body')
		        .prepend('<div class="alert alert-info fade in">' +
		          'Updated!<button type="button" class="close" data-dismiss="alert"></button>' +
		        '</div>');
		  }, 1000);
		});
       
    }

    return {
        //main function to initiate the module
        init: function () {
            initModals();
        }

    };

}();

