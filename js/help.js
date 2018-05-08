/* global Mustache, _ */
;(function($) {
  
  var Help = {
    
    isEnabled: function() {
      return $('.help').length === 1;
    },
    
    show: function(selector) {
      var context = $(selector);
      context.addClass('contains-help');
      context.append(Mustache.render($('#help-template').html()));
      context.trigger('help');
    },
    
    add: function(hotspot) {
      var element = $(Mustache.render($('#help-hotspot-template').html(), hotspot));
      
      element.data('config', hotspot);
      
      $('.contains-help').append(element);
      
      Help.update(element);
    },
    
    update: function(hotspot) {
      var config = hotspot.data('config');
      var anchor = null;
      
      if (!!config['handler']) {
        anchor = config['handler']();
      } else {
        var element = $(config.selector);
        if (element.is(':visible') && element.get(0).getBoundingClientRect().width !== 0) {
          anchor = {
            x: element.offset().left,
            y: element.offset().top,
            w: element.get(0).getBoundingClientRect().width,
            h: element.get(0).getBoundingClientRect().height
          };
        }
      }

      if (!anchor) {
        return;
      }
      
      var xPadding = 16;
      var yPadding = 16;
      
      if ('padding' in config && typeof config['padding'] === 'number') {
        xPadding = config.padding;
        yPadding = config.padding;
      }
      
      if ('padding' in config && typeof config['padding'] === 'object') {
        var xPadding = config.padding[0];
        var yPadding = config.padding[1];
      }
      
      hotspot.css({
        left: anchor.x - (xPadding / 2),
        top: anchor.y - (yPadding / 2)
      });

      hotspot.find('.anchor').css({
        'width': anchor.w + xPadding,
        'height': anchor.h + yPadding,
        'border-radius': !!config['rounded'] ? anchor.w + xPadding : 0
      });
    },
    
    refresh: function() {
      $('.contains-help .help-hotspot').each(function() {
        Help.update($(this));
      });
    },
    
    close: function() {
      $('.contains-help .help-hotspot').remove();
      $('.contains-help').removeClass('contains-help');
      $('.help').remove();
    }
    
  };
  
  $(document).on('click', '.toggles-help[data-context]', function(e) {
    if (!!e.preventDefault) e.preventDefault();

    Help.show($(this).attr('data-context'));

    return false;
  });
  
  $(document).on('click', '.help a.close', function(e) {
    if (!!e.preventDefault) e.preventDefault();

    Help.close();

    return false;
  });
  
  $(document).on('ready', function() {
    $(window).on('resize', _.throttle(Help.refresh, 200));
  });
  
  window['Help'] = Help;
  
})(jQuery);