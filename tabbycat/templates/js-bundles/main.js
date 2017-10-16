// The base template with universal or near-universal functionality (imported on all pages)

//------------------------------------------------------------------------------
// jQuery, Lodash, and Boostrap
//------------------------------------------------------------------------------

var $ = require("jquery");
global.jQuery = $; // Set for bootstrap
window.$ = $; // Set for browser window

// Hover over options Needs to come before bootstrap
import Popper from 'popper.js';
window.Popper = Popper;

// Import bootstrap javascript plugins
require("bootstrap");

// Icons
import feather from 'feather-icons';

// Polyfill Safari support for datalists (ballot checkins + constraints import)
require("datalist-polyfill");

// Add alerts programmatically
$.fn.extend({
  showAlert: function(alerttype, message, timeout) {
    $('#messages-container').append('<div id="alertdiv" class="alert alert-' + alerttype + ' fade show"><button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button><span>' + message + '</div>');
    if (timeout && timeout !== 0) {
      setTimeout(function() { // this will automatically close the alert and remove this if the users doesnt close it in 5 secs
        $("#alertdiv").alert('close');
      }, timeout);
    }
  },
  loadButton: function(button) {
    // Can't use disable attr as some submission button need to pass their value
    $(button).addClass("disabled");
  },
  resetButton: function(button) {
    $(button).removeClass("disabled");
  }
});

// Mount global jquery stuff here
$(document).ready(function(){

  // Enable hover tooltips for all elements
  $('[data-toggle=tooltip]').tooltip({
    'html': true
  });
  // Make larger click targets for checkboxes in tables
  $('.checkbox-target').on('click', function (e) {
    if (e.target === this) { // Don't trigger when clicking the input itself
      var checkBox = $("input[type=checkbox]", this).first();
      checkBox.prop("checked", !checkBox.prop("checked"));
      checkBox.trigger("change");
    }
  });
  // Feather shim for icons
  feather.replace();
  // Remove the pre-expanded sidebar states for mobile (they overlap)
  if ($(window).width() < 768) {
    $("#sidebar .collapse").removeClass("show");
  };

  // Auto disable submit buttons for forms upon submission (prevent double-sub)
  $('form').submit(function(event){
    $("[type=submit]", this).each(function(){
      $.fn.loadButton(this);
    });
  });

});

//------------------------------------------------------------------------------
// Vue Structure Setup
//------------------------------------------------------------------------------

// Setup the main constructs used for custom components
var vueComponents = {}

// This is the main data package setout in the django template
var vueData = window.vueData // We need to mount props from the window itself

//------------------------------------------------------------------------------
// Vue Shared Components Setup
//------------------------------------------------------------------------------

// Table-based Views
import TablesContainer from '../tables/TablesContainer.vue'
vueComponents['TablesContainer'] = TablesContainer

// Diversity Standings
import DiversityContainer from  '../js-vue/containers/DiversityContainer.vue'
vueComponents['DiversityContainer'] = DiversityContainer

//------------------------------------------------------------------------------
// Expose data for admin/public.js to import
//------------------------------------------------------------------------------

// For admin modules
export default {
  baseComponents: vueComponents,
  baseData: vueData,
}
