/* global Contents, d3, Mustache, Waypoint */
;(function($) {

  var tooltip = $('<div/>');
  tooltip.attr('id', 'hirings-tooltip');
  tooltip.css('visibility', 'hidden');
  tooltip.appendTo('body');

  function drawHiringsChart(container, dataset, options, callback) {
    var svg = d3.select(container);

    svg.selectAll('*').remove();

    var g = svg.append('g')
      .attr('transform', 'translate(0, -24)');

    var width = $(container).width();
    var height = $(container).height() - 24;

    var x = d3.scaleBand()
      .rangeRound([0, width])
      .align(0.1);

    var y = d3.scaleLinear()
      .rangeRound([height, 0]);

    x.domain(dataset.map(function(d) {
      return d.year;
    }));

    y.domain([options.values.minimum, options.values.maximum]).nice();

    var xAxis = d3.axisBottom()
      .scale(x)
      .tickPadding(8)
      .tickSize(0)
      .tickValues([
        d3.min(dataset, function(d) {
          return d.year;
        }),
        d3.max(dataset, function(d) {
          return d.year;
        })
      ]);

    var yAxis = d3.axisLeft()
      .scale(y)
      .tickSize(-width, 0, 0)
      .tickFormat('');

    g.append('g')
      .attr('opacity', '0')
      .attr('height', '24')
      .attr('class', 'axis axis--x')
      .attr('transform', 'translate(0, ' + height + ')')
      .call(xAxis)
      .transition()
      .duration(options.duration)
      .delay(options.initialDelay)
      .attr('opacity', '1');

    g.append('g')
      .attr('opacity', '0')
      .attr('class', 'axis axis--y')
      .transition()
      .duration(options.duration)
      .delay(options.initialDelay)
      .call(yAxis)
      .attr('opacity', '1');

    var stack = d3.stack();

    var gender = g.selectAll('.gender')
      .data(stack.keys(['male', 'female'])(dataset))
      .enter()
      .append('g')
      .attr('class', function (d, i) {
        var classes = [];
        classes.push('gender');

        if (i === 0) {
          classes.push('male');
        }

        if (i === 1) {
          classes.push('female');
        }

        return !!classes ? classes.join(' ') : null;
      });

    var rects = gender.selectAll('rect')
      .data(function(d) {
        return d;
      })
      .enter()
      .append('rect')
      .attr('data-year', function(d) {
        return d.data.year;
      })
      .on('mouseover', function(d) {
        tooltip.html(Mustache.render($('#hirings-tooltip-template').html(), {
          year: d.data.year,
          values: [
            {
              name: Contents.hirings.tooltip.hired,
              value: (d.data.female + d.data.male)
            },
            {
              name: Contents.hirings.tooltip.female,
              value: d.data.female
            },
            {
              name: Contents.hirings.tooltip.male,
              value: d.data.male
            }
          ]
        }));

        tooltip.css('visibility', 'visible');

        $(container).addClass('contains-highlights');
        $(container).find('rect[data-year="' + d.data.year + '"]').addClass('is-highlighted');
      })
      .on('mousemove', function(d) {
        tooltip.css({
          left: d3.event.pageX,
          top: d3.event.pageY
        });
      })
      .on('mouseout', function(d) {
        tooltip.css('visibility', 'hidden');

        $(container).removeClass('contains-highlights');
        $(container).find('rect[data-year]').removeClass('is-highlighted');
      });

    rects
      .attr('x', function(d) {
        return x(d.data.year);
      })
      .attr('y', function(d) {
        return height;
      })
      .attr('height', function(d) {
        return 0;
      })
      .attr('width', x.bandwidth())
      .transition()
      .duration(options.initialDelay)
      .delay(function (d, i) {
				return i * options.delay;
			})
      .attr('y', function(d) {
        return y(d[1]);
      })
      .attr('height', function(d) {
        return y(d[0]) - y(d[1]);
      });

    if (!!callback) callback();
  }

  function createHelp() {
    var element = $('#hirings-charts .contains-hirings-chart:eq(1)');

    Help.add({
      handler: function() {
        var title = element.siblings('h3').find('span');

        return {
          x: title.offset().left,
          y: title.offset().top,
          w: title.width(),
          h: title.height()
        };
      },
      alignment: 'right',
      padding: [32, 16],
      text: Contents.hirings.help.centre
    });

    Help.add({
      handler: function() {
        var biggestFemales = $(_.sortBy(element.find('g.female rect'), function(t) { return $(t).offset().top; }));

        var year = $(biggestFemales[0]).data('year');

        var maleCounterpart = element.find('g.male rect[data-year="' + year + '"]');

        var femaleRect = biggestFemales[0].getBoundingClientRect();
        var maleRect = maleCounterpart[0].getBoundingClientRect();

        return {
          x: $(biggestFemales[0]).offset().left,
          y: $(biggestFemales[0]).offset().top,
          w: femaleRect.width,
          h: (femaleRect.height + maleRect.height)
        };
      },
      alignment: 'right',
      text: Contents.hirings.help.hired
    });

    Help.add({
      handler: function() {
        var text = element.find('.axis--x .tick:first');
        var rect = text[0].getBoundingClientRect();

        return {
          x: text.offset().left + (rect.width / 2) - 16,
          y: text.offset().top + (rect.height / 2) - 16,
          w: 32,
          h: 32
        };
      },
      alignment: 'left',
      rounded: true,
      text: Contents.hirings.help.from
    });

    Help.add({
      handler: function() {
        var text = element.find('.axis--x .tick:last');
        var rect = text[0].getBoundingClientRect();

        return {
          x: text.offset().left + (rect.width / 2) - 16,
          y: text.offset().top + (rect.height / 2) - 16,
          w: 32,
          h: 32
        };
      },
      alignment: 'right',
      rounded: true,
      text: Contents.hirings.help.until
    });
  }

  $.get('./data/hirings.json').done(function(response) {
    var years = [];
    var values = [];
    var charts = [];

    for (var i = 0; i < response.length; i++) {
      $.each(response[i].data, function(k, d) {
        years.push(d.year);
        values.push(d.female + d.male);
      });

      var chart = $.extend(response[i], {
        cid: 'hirings-' + Math.random().toString(36).substring(7)
      });

      charts.push(chart);
    }

    $('#hirings-charts')
      .empty()
      .append(Mustache.render($('#hirings-template').html(), {
        charts: charts
      }));

    var options = {
      years: {
        minimum: d3.min(years),
        maximum: d3.max(years)
      },
      values: {
        minimum: 0,
        maximum: d3.max(values)
      }
    };

    new Waypoint({
      offset: '50%',
      element: $('#hirings-charts').get(0),
      handler: function() {
        $.each(charts, function(i, chart) {
          var selector = '#' + chart.cid;

          setTimeout(function() {
            var years = {};

            $.each(chart.data, function(i, d) {
              years[d.year] = d;
            });

            var data = [];

            for (var year = options.years.minimum; year <= options.years.maximum; year++) {
              if (year in years) {
                data.push(years[year]);
              } else {
                data.push({ year: year, female: 0, male: 0 });
              }
            }

            drawHiringsChart(selector, data, $.extend(options, {
              duration: 240,
              delay: 32,
              initialDelay: 320
            }), function() {
              $(selector).addClass('has-been-rendered');
            });
          }, i * 50);
        });

        $(window).on('resize', _.throttle(function() {
          $.each(charts, function(i, chart) {
            var selector = '#' + chart.cid;

            var years = {};

            $.each(chart.data, function(i, d) {
              years[d.year] = d;
            });

            var data = [];

            for (var year = options.years.minimum; year <= options.years.maximum; year++) {
              if (year in years) {
                data.push(years[year]);
              } else {
                data.push({ year: year, female: 0, male: 0 });
              }
            }

            drawHiringsChart(selector, data, $.extend(options, {
              duration: 0,
              delay: 0,
              initialDelay: 0
            }));
          });
        }, 200));

        setTimeout(function() {
          if (Help.isEnabled()) {
            setTimeout(function() {
              createHelp();
            }, 250);
          }

          $('body').on('help', function() {
            createHelp();
          });
        }, charts.length * 100);

        this.disable();
      }
    });
  });

})(jQuery);
