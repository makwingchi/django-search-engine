jQuery.fn.pagination = function(maxentries, opts) {
	opts = jQuery.extend({
				items_per_page : 10,
				current_page : 0,
				num_display_entries : 4,
				num_edge_entries : 2,
				link_to : "javascript:;",
				prev_text : "Previous",
				next_text : "Next",
				ellipse_text : "...",
				display_msg : true,
				prev_show_always : true,
				next_show_always : true,
				setPageNo:false,
				callback : function() {
					return false;
				}
			}, opts || {});

	return this.each(function() {
		// total pages
		function numPages() {
			return Math.ceil(maxentries / opts.items_per_page);
		}
		/**
		 * calculate number of pages
		 */
		function getInterval() {
			var ne_half = Math.ceil(opts.num_display_entries / 2);
			var np = numPages();
			var upper_limit = np - opts.num_display_entries;
			var start = current_page > ne_half ? Math.max(Math.min(current_page
									- ne_half, upper_limit), 0) : 0;
			var end = current_page > ne_half ? Math.min(current_page + ne_half,
					np) : Math.min(opts.num_display_entries, np);
			return [start, end];
		}

		/**
		 * click event
		 */
		function pageSelected(page_id, evt) {
			var page_id = parseInt(page_id);
			current_page = page_id;
			drawLinks();
			var continuePropagation = opts.callback(page_id, panel);
			if (!continuePropagation) {
				if (evt.stopPropagation) {
					evt.stopPropagation();
				} else {
					evt.cancelBubble = true;
				}
			}
			return continuePropagation;
		}

		/**
		 * links
		 */
		function drawLinks() {
			panel.empty();
			var interval = getInterval();
			var np = numPages();
			var getClickHandler = function(page_id) {
				return function(evt) {
					return pageSelected(page_id, evt);
				}
			}
			var appendItem = function(page_id, appendopts) {
				page_id = page_id < 0 ? 0 : (page_id < np ? page_id : np-1);
				appendopts = jQuery.extend({
							text : page_id+1,
							classes : ""
						}, appendopts || {});
				if (page_id == current_page) {
					var lnk = $("<span class='current'>" + (appendopts.text)
							+ "</span>");
				} else {
					var lnk = $("<a>" + (appendopts.text) + "</a>").bind(
							"click", getClickHandler(page_id)).attr('href',
							opts.link_to.replace(/__id__/, page_id));

				}
				if (appendopts.classes) {
					lnk.addClass(appendopts.classes);
				}
				panel.append(lnk);
			}
			// previous page
			if (opts.prev_text && (current_page > 0 || opts.prev_show_always)) {
				appendItem(current_page - 1, {
							text : opts.prev_text,
							classes : "prev"
						});
			}
			// ...
			if (interval[0] > 0 && opts.num_edge_entries > 0) {
				var end = Math.min(opts.num_edge_entries, interval[0]);
				for (var i = 0; i < end; i++) {
					appendItem(i);
				}
				if (opts.num_edge_entries < interval[0] && opts.ellipse_text) {
					jQuery("<span>" + opts.ellipse_text + "</span>")
							.appendTo(panel);
				}
			}
			// interval page
			for (var i = interval[0]; i < interval[1]; i++) {
				appendItem(i);
			}
			// last page
			if (interval[1] < np && opts.num_edge_entries > 0) {
				if (np - opts.num_edge_entries > interval[1]
						&& opts.ellipse_text) {
					jQuery("<span>" + opts.ellipse_text + "</span>")
							.appendTo(panel);
				}
				var begin = Math.max(np - opts.num_edge_entries, interval[1]);
				for (var i = begin; i < np; i++) {
					appendItem(i);
				}

			}
			// next page
			if (opts.next_text
					&& (current_page < np - 1 || opts.next_show_always)) {
				appendItem(current_page + 1, {
							text : opts.next_text,
							classes : "next"
						});
			}
			// records
			if (opts.display_msg) {
				if(!maxentries){
					panel.append('<div class="pxofy">No Records</div>');
				}else{
					panel.append();
				}
			}
			// jump to which page
			if(opts.setPageNo){
				  panel.append("<div class='goto'><span class='text'>Jump to </span><input type='text'/><span class='page'>page</span><button type='button' class='ue-button long2'>Confirm</button></div>");
			}
		}

		// current page
		var current_page = opts.current_page;
		maxentries = ( maxentries < 0) ? 0 : maxentries;
		opts.items_per_page = (!opts.items_per_page || opts.items_per_page < 0)
				? 1
				: opts.items_per_page;
		var panel = jQuery(this);
		this.selectPage = function(page_id) {
			pageSelected(page_id);
		}
		this.prevPage = function() {
			if (current_page > 0) {
				pageSelected(current_page - 1);
				return true;
			} else {
				return false;
			}
		}
		this.nextPage = function() {
			if (current_page < numPages() - 1) {
				pageSelected(current_page + 1);
				return true;
			} else {
				return false;
			}
		}
		
		if(maxentries==0){
			panel.append('<span class="prev">'+opts.prev_text+'</span><span class="current next">'+opts.next_text+'</span><div class="pxofy">No matching records</div>');
		}else{
			drawLinks();
		}
		$(this).find(".goto button").live("click",function(evt){
			var setPageNo = $(this).parent().find("input").val();
			if(setPageNo!=null && setPageNo!=""&&setPageNo>0&&setPageNo<=numPages()){
				pageSelected(setPageNo-1, evt);
			}
		});		
	});
}
