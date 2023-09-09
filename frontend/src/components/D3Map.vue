<template lang="html">
	<div class="svg-wrapper"></div>
</template>

<script>
	import * as d3 from 'd3'
	import * as topojson from 'topojson'
	import raw from '../assets/indonesia.json'

	export default {
		name: 'D3Map',
		data: () => ({
			canvas: null,
			tooltip: null,
			startcolor: '#FFF',
			endcolor: '#DE3246',
			size: {
				width: 0,
				height: 0,
			},
			min: 0,
			max: 0,
		}),
		props: ['data'],
		methods: {
			initCanvas: function() {
				return new Promise((resolve, reject) => {
					d3.select(this.$el).selectAll('svg').remove();

					this.size.width		= this.$el.clientWidth;
					this.size.height	= this.$el.clientWidth / 1.618;

					let svg	= d3.select(this.$el)
						.append('svg')
						.attr('width', this.size.width)
						.attr('height', this.size.height);

					this.canvas		= svg.append('g').attr('id', 'canvas').attr('transform', 'translate(0,0)');
					this.tooltip	= svg.append('g').attr('id', 'tooltip').attr('transform', 'translate(0,0)').attr('class', 'hidden');

					this.tooltip.append('rect').attr('rx', 5).attr('ry', 5);
					this.tooltip.append('text');

					let projection	= d3.geoMercator()
						.scale(this.size.width * 1.15)
						.center([118, -1.85])
						.translate([this.size.width / 2, this.size.height / 2.5]);

					let path		= d3.geoPath().projection(projection);

					let topo		= topojson.feature(raw, raw.objects.map);
					let mappedGeo	= _.chain(topo).get('features', []).keyBy('properties.id_provinsi').mapValues((o) => ({ centroid: path.centroid(o), bounds: path.bounds(o) })).value();

					let elems		= this.canvas.append('g').attr('id', 'prov-wrapper').selectAll('g.province').data(topo.features).enter().append('g')
						.attr('id', o => 'prov-' + o.properties.id_provinsi)
						.attr('class', 'province')
						.on('mouseover', o => { this.onMouseover(o.properties.id_provinsi, o.properties.nm_provinsi); })
						.on('mouseout', this.onMouseout)
						.on('mousemove', this.onMousemove);

					elems.append('path')
						.attr('d', path)
						.attr('class', '')
						.attr('vector-effect', 'non-scaling-stroke')
						.style('stroke-width', '.5px');

					elems.append('text')
						.attr('x', (o) => (mappedGeo[o.properties.id_provinsi].centroid[0]))
						.attr('y', (o) => (mappedGeo[o.properties.id_provinsi].centroid[1]))
						.attr('class', 'hidden')
						.style('font-size', 11 + 'px')
						.text((o) => (o.properties.nm_provinsi));

					resolve();
				});
			},
			colorMap: function() {
				let colorFunc	= d3.scaleLinear().domain([this.min, this.max]).range([this.startcolor, this.endcolor]);

				this.data.forEach(o => { this.canvas.select('g#prov-' + o.prov_id).style('fill', colorFunc(o.value)); });
			},
			createLegend: function() {
				let width	= this.size.width * .9;
				let height	= this.size.height * .05;

				this.canvas.selectAll('defs, #legend-canvas').remove();

				this.canvas.append('defs').append('linearGradient')
					.attr('id', 'gradient')
					.attr('x1', '0%').attr('y1', '0%')
					.attr('x2', '100%').attr('y2', '0%')
					.selectAll('stop')
					.data([this.startcolor, this.endcolor])
					.enter().append("stop")
					.attr("offset", (d,i) => (i) )
					.attr("stop-color", (d) => (d));

				let legend	= this.canvas.append('g')
					.attr('id', 'legend-canvas')
					.attr('transform', 'translate(' + (this.size.width * 0.05) + ',' + (this.size.height * .85) + ')');

				legend.append('rect')
					.attr('x', '0')
					.attr('y', '0')
					.attr('width', width)
					.attr('height', height)
					.attr('fill', 'url(#gradient)');

				let scale	= d3.scaleLinear().domain([this.min, this.max]).range([0, width]);
				legend.append('g')
					.attr('class', 'axis')
					.attr('transform', 'translate(0,' + height + ')')
					.call(d3.axisBottom(scale).ticks(4));

			},
			onMousemove: function() {
				let mouse		= d3.mouse(this.canvas.node());

				let bbox		= this.tooltip.node().getBoundingClientRect();
				let xPosition	= mouse[0] - (bbox.width / 2);
				let yPosition	= mouse[1] - bbox.height - 5;

				this.tooltip.attr('transform', 'translate(' + xPosition + ',' + yPosition + ')');
			},
			onMouseover: function(id, nm) {
				this.tooltip.classed('hidden', false);

				let value		= _.chain(this.data).find(['prov_id', '' + id]).get('value', 0).value();
				this.tooltip.select('text').text(nm + ': ' + value);

				let bbox		= this.tooltip.select('text').node().getBoundingClientRect();
				this.tooltip.select('rect')
					.attr('x', -10)
					.attr('y', -bbox.height)
					.attr('width', bbox.width + 20)
					.attr('height', bbox.height + 7.5)
			},
			onMouseout: function() { this.tooltip.classed('hidden', true); },
			refreshMap: function() {
				this.min	= d3.min(this.data, o => o.value);
				this.max	= d3.max(this.data, o => o.value);

				this.colorMap();
				this.createLegend();
			}
		},
		mounted: async function() {
			await this.initCanvas();
			this.refreshMap();
		},
		// watch: {
		// 	data: { immediate: true, handler (val, oldVal) {
		// 			console.log(val);
		// 		}
		// 	}
		// },
	}
</script>

<style lang="scss">
	.svg-wrapper svg {
		g#canvas {
			g.province {
				fill: transparent; stroke: $magenta;
			}
			.axis {
				path, .tick line { stroke: #888888; }
				.tick text { fill: #888888; }
			}
		}
		g#tooltip {
			text { font-size: 11px; fill: white; }
			rect { fill: $magenta; opacity: .75; }
		}
	}
</style>
