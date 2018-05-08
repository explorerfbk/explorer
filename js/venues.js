/* global Mustache, Waypoint */
;(function($) {

  var CLOUD_OFFSETS = [ '', 'is-top', 'is-bottom' ];
  var CLOUD_SIZES = [ '', 'is-small', 'is-big' ];
  var CLOUD_SPEEDS = [ '', 'is-slow', 'is-fast' ];
  var CLOUD_LAYERS = [ '', 'is-front' ];

  function shuffle(array) {
    let counter = array.length;

    while (counter > 0) {
        let index = Math.floor(Math.random() * counter);

        counter--;

        let temp = array[counter];
        array[counter] = array[index];
        array[index] = temp;
    }

    return array;
  }

  function renderVenues(container, venues) {
    container.empty();

    $.each(venues, function(i, venue) {
      var clouds = [];

      if (!venue.type || venue.type === 'outdoor') {
        var sizes = shuffle(CLOUD_SIZES.concat([]));
        var numberOfClouds = Math.floor(Math.random() * sizes.length);

        for (var i = 0; i < numberOfClouds; i++) {
          clouds.push({
            offset: CLOUD_OFFSETS[Math.floor(Math.random() * CLOUD_OFFSETS.length)],
            size: sizes.shift(),
            speed: CLOUD_SPEEDS[Math.floor(Math.random() * CLOUD_SPEEDS.length)],
            layer: CLOUD_LAYERS[Math.floor(Math.random() * CLOUD_LAYERS.length)]
          });
        }
      }

      container.append(Mustache.render($('#venue-template').html(), $.extend(venue, { clouds: clouds })));
    });

    container.find('span[data-number]').each(function() {
      $(this).animateNumber({
        number: $(this).attr('data-number')
      });
    });
  }

  $(document).on('ready', function() {
    $.get('./data/venues.json').done(function(dataset) {
      var years = $.map(dataset, function(dataset, index) {
        return index;
      });

      var defaultYear = years[years.length - 1];
      var currentYear = null;

      function updateYear(year) {
        currentYear = year;

        renderVenues($('#venues-container'), dataset[String(currentYear)]);

        var index = $.inArray(String(year), years);

        $('#venues-year-switcher .current-year').text(currentYear);
        $('#venues-year-switcher .previous').toggleClass('disabled', index === 0 ? true : false);
        $('#venues-year-switcher .next').toggleClass('disabled', index === (years.length - 1) ? true : false);
      }

      $(document).on('click', '#venues-year-switcher .previous:not(.disabled)', function() {
        var index = $.inArray(String(currentYear), years);
        if (index > 0) {
          updateYear(years[index - 1]);
        }
      });

      $(document).on('click', '#venues-year-switcher .next:not(.disabled)', function() {
        var index = $.inArray(String(currentYear), years);
        if (index < (years.length - 1)) {
          updateYear(years[index + 1]);
        }
      });

      $('#venues-year-switcher .current-year').text(defaultYear);
      $('#venues-year-switcher .previous').addClass('disabled');
      $('#venues-year-switcher .next').addClass('disabled');

      updateYear(defaultYear);
    });
  });

})(jQuery);