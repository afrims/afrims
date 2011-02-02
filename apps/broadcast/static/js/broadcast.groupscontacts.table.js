/**
 * Created by IntelliJ IDEA.
 * User: adewinter
 * Date: Jan 31, 2011
 * Time: 4:55:57 PM
 * To change this template use File | Settings | File Templates.
 */
var ocTable;
var ogTable;
var contactsSelected =  [];
var groupsSelected = [];
function init_groups_and_contacts_tables(){
    ////////Contact and Group Table setup
	ogTable = $('#groups_table').dataTable( {
		"bProcessing": true,
		"bServerSide": true,
		"bPaginate"      : true,
		"sPaginationType": "full_numbers",
		"bAutoWidth": false,
		"bJQueryUI": true,
		"sAjaxSource": "groups_table/",
		"fnRowCallback": function( nRow, aData, iDisplayIndex ) {
			if ( jQuery.inArray(aData[0], groupsSelected) != -1 )
			{
				$(nRow).addClass('row_selected');
			}
			return nRow;
		},
		"aoColumns": [
			{ "bVisible": 0 }, /* ID column */
			null,
			null,
		]
	});




	ocTable = $('#contacts_table').dataTable( {
		"bProcessing": true,
		"bServerSide": true,
		"bPaginate"      : true,
		"bAutoWidth": false,
		"sPaginationType": "full_numbers",
		"bJQueryUI": true,
		"sAjaxSource": "contacts_table/",
		"fnRowCallback": function( nRow, aData, iDisplayIndex ) {
			if ( jQuery.inArray(aData[0], contactsSelected) != -1 )
			{
				$(nRow).addClass('row_selected');
			}
			return nRow;
		},
		"aoColumns": [
			{ "bVisible": 0 }, /* ID column */
			null,
			null,
			{ "bVisible": 0 },
			null,
		]
	});

	/* Click event handler */
	$('#contacts_table tbody tr').live('click', function () {
		var aData = ocTable.fnGetData( this );
		var iId = aData[0];

		if ( jQuery.inArray(iId, contactsSelected) == -1 )
		{
			contactsSelected[contactsSelected.length++] = iId;
		}
		else
		{
			contactsSelected = jQuery.grep(contactsSelected, function(value) {
				return value != iId;
			} );
		}

		$(this).toggleClass('row_selected');
        $('#id_contacts').val(contactsSelected)
	} );

		/* Click event handler */
	$('#groups_table tbody tr').live('click', function () {
		var aData = ogTable.fnGetData( this );
		var iId = aData[0];

		if ( jQuery.inArray(iId, groupsSelected) == -1 )
		{
			groupsSelected[groupsSelected.length++] = iId;
		}
		else
		{
			groupsSelected = jQuery.grep(groupsSelected, function(value) {
				return value != iId;
			} );
		}

		$(this).toggleClass('row_selected');
        $('#id_groups').val(groupsSelected)
	} );

	$('#contacts_search_box').keyup(function() {
  		 ocTable.fnFilter($('#contacts_search_box').val());
	});

	$('#groups_search_box').keyup(function() {
  		 ogTable.fnFilter($('#groups_search_box').val());
	});



    //remove the freaking header banner from the tables
    $('#contacts_table_wrapper .ui-widget-header:first').addClass('nullity')
    $('#groups_table_wrapper .ui-widget-header:first').addClass('nullity')

    $('#contacts_table_wrapper .ui-widget-header:last').addClass('table_footer')
    $('#groups_table_wrapper .ui-widget-header:last').addClass('table_footer')


    //Add submit handler to the form to grab the selected contacts from the groups and/or contacts table
    //and populate the groups and/or contacts FormFields respectively

    $('#broadcast_form').submit(function(){
//        alert('GROUPS:'+groupsSelected+'||CONTACTS:'+contactsSelected)

       alert('GROUPS:'+$('#id_groups').val()+'||CONTACTS:'+$('#id_contacts').val())
    });
}