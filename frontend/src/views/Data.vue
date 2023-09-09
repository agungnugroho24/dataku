2<template lang="html">
	<div id="datapage">
		<header>
			<div class="wrapper">
				<div id="blurp">temukan data lain di <span class="cursor-pointer" @click="$router.push({ name: 'home' })">dataku<b>ID</b></span>:</div>
				<!-- <input type="text" v-model="search" placeholder="type here to find data by theme (min. 3 characters)"> -->
				<vue-single-select @input="onCateClick" max-height="350px" v-model="search" :options="typeaheadVal" optionLabel="name" class="typeahead" placeholder="Cari berdasarkan tema (min. 3 karakter)"></vue-single-select>
				<div id="icon-wrapper"><font-awesome-icon icon="search" /></div>
			</div>
		</header>

		<section id="summary" class="noselect">
			<div id="summary-wrapper">
				<div id="summary-title">{{ summary.name }}</div>
				<div id="summary-drops">
					<div class="drops-wrapper">
						<label>Daerah</label>
						<Dropdown id="daerah" ref="region" class="placeholder cursor-pointer" :list="summary.list.region" @dropchange="ondropchange($event, 'region')"></Dropdown>
					</div>
					<div class="drops-wrapper">
						<label>Periode</label>
						<Dropdown id="start-year" ref="start" class="placeholder cursor-pointer" :list="summary.list.start" pick-last @dropchange="ondropchange($event, 'start')"></Dropdown>
						<div class="divider">-</div>
						<Dropdown id="end-year" ref="end" class="placeholder cursor-pointer" :list="summary.list.end" @dropchange="ondropchange($event, 'end')"></Dropdown>
					</div>
				</div>
				<div id="summary-stats">
					<div class="summary-stat-wrapper" v-for="stat in summary.stats">
						<div class="summary-left">{{ stat[0] }}</div>
						<div class="summary-right">
							<div class="summary-stat-value">{{ formatNumeric(stat[1]) }}</div>
							<div class="summary-stat-unit">{{ stat[2] }}</div>
						</div>
					</div>
				</div>
				<div id="summary-another" class="cursor-pointer" @click="onSummaryChange" :class="{ onload: summary.load }">
					<span v-if="!summary.load">tampilkan risalah lain</span>
					<font-awesome-icon icon="circle-notch" spin v-if="summary.load"/>
				</div>
			</div>
		</section>

		<div class="paginate-wrapper noselect">
			<paginate v-model="paginateOpts.page" :page-count="pageCount" :click-handler="onPageChange" :prev-text="'&laquo;'" :next-text="'&raquo;'" :container-class="'pagination'"></paginate>
			<div class="search-wrap">
				<input type="text" v-model="filterkey" placeholder="filter untuk dataset">
				<font-awesome-icon icon="search" />
			</div>
		</div>

		<section v-if="shown.length > 0" class="datasets" v-for="o in shown">
			<div class="detail-wrapper">
				<div class="detail-title">{{ o.title }}</div>
				<div class="detail-year">Tahun {{ o.year }}</div>
				<div class="detail-desc">{{ o.desc }}</div>
				<div class="button-wrapper" :class="{ map: isMap(o.is_map, o.type) }">
					<a class="button-download cursor-pointer" :href="constructLink(o.table_id)" target="_blank">
						<div class="svg-wrapper"><Unduhdata></Unduhdata></div>
						<span>Unduh data</span>
					</a>
					<div class="button-show cursor-pointer" @click="$modal.show('modal-table', { id: o.table_id, title: o.title })">
						<div class="svg-wrapper"><Lihatdata></Lihatdata></div>
						<span>Lihat data</span>
					</div>
					<div v-if="isMap(o.is_map, o.type)" class="button-map cursor-pointer" @click="$modal.show('modal-map', { id: o.table_id, title: o.title, variable: o.variable, region: summary.selected.region })">
						<div class="svg-wrapper"><Showmap></Showmap></div>
						<span>Lihat Map</span>
					</div>
				</div>
			</div>
			<div class="chart-wrapper">
				<D3Map v-if="o.type == 'Map'" :data="o.data"></D3Map>
				<chartist v-else :ratio="chartsRatio[o.type]" :type="o.type" :data="o.data" :options="chartsOpt[o.type]" ></chartist>
			</div>
		</section>

		<section v-if="shown.length == 0" id="nodata" class="noselect">Tidak ada data yang tersedia.</section>

		<div class="paginate-wrapper noselect">
			<paginate v-model="paginateOpts.page" :page-count="pageCount" :click-handler="onPageChange" :prev-text="'&laquo;'" :next-text="'&raquo;'" :container-class="'pagination'"></paginate>
			<div class="search-wrap">
				<input type="text" v-model="filterkey" placeholder="filter untuk dataset">
				<font-awesome-icon icon="search" />
			</div>
		</div>

		<footer></footer>
		<modal-table/>
		<modal-map/>
	</div>
</template>

<script>
	import axios from 'axios'
	import modalMap from '@/modals/Map.vue'
	import D3Map from '@/components/D3Map.vue'
	import modalTable from '@/modals/Table.vue'
	import Dropdown from '@/components/Dropdown.vue'
	import * as ChartistTooltips from 'chartist-plugin-tooltips'

	export default {
		name: 'Data',
		data: function() { return({
			search: '',
			typeaheadVal: [],
			summary: {
				list: {
					region: [],
					start: [],
					end: [],
					years: [],
				},
				selected: {
					region: null,
					start: null,
					end: null,
				},
				name: "",
				stats: [],
				load: false,
			},
			filterkey: '',
			datasets: [],
			shown: [],
			paginateOpts: {
				page: 1,
				perPage: 6,
				stepLimit: 2,
			},
			chartsOpt: {
				'Line'	: { showArea: true, axisY: { onlyInteger: true }, plugins: [this.$chartist.plugins.tooltip()] },
				'Bar'	: { axisY: { onlyInteger: true }, plugins: [this.$chartist.plugins.tooltip()] },
				'Pie'	: { plugins: [this.$chartist.plugins.tooltip()] },
			},
			chartsRatio: {
				'Line'	: 'ct-golden-section',
				'Bar'	: 'ct-golden-section',
				'Pie'	: 'ct-golden-section',
			}
		}); },
		methods : {
			isMap: function(bool, type) { return bool && (type !== 'Map'); },
			ondropchange: function(val, state) {
				this.summary.selected[state]	= val.val;
				if (state == 'end') { this.summary.list.start = _.pickBy(this.summary.list.years, o => (parseInt(o) <= parseInt(val.val))); }
				if (state == 'start') { this.summary.list.end = _.pickBy(this.summary.list.years, o => (parseInt(o) >= parseInt(val.val))); }

				const { region, start, end } = this.summary.selected;
				let params	= _.omitBy({ region, start_year: start, end_year: end }, _.isNull);

				this.datasets		= [];
				axios.get(this.$store.state.baseURL + 'subjects/' + this.$route.params.id, { params })
					.then(response => {
						this.summary.stats	= response.data.summary;
						this.datasets		= response.data.graphs;
					})
					.catch(err => { console.error(err.response); })
			},
			onSummaryChange: function() {
				if (!this.summary.load) {
					this.summary.load	= true;

					const { region, start, end } = this.summary.selected;
					let params	= _.omitBy({ region, start_year: start, end_year: end }, _.isNull);

					axios.get(this.$store.state.baseURL + 'stats/' + this.$route.params.id, { params })
					.then(response => {
						this.summary.stats	= response.data.summary;
						this.summary.load	= false;
					})
					.catch(err => { console.error(err.response); })
				}
			},
			onPageChange: function(o) { this.changeShown() },
			onCateClick: function(o) { if (o) { this.$router.push({ name: 'data', params: { id: o.id } }) } },
			formatNumeric: function(val) {
				if (_.includes(val, '%')) { return val; } else {
					let rounded = _.round(val, 2).toString();

					return _.chain(val).round(2).split('.').map((o, i) => ((i == 0) ? o.replace(/\B(?=(\d{3})+(?!\d))/g, ",") : o)).join('.').value()
				}
			},
			constructLink: function(id) { return this.$store.state.baseURL + 'download/' + id; },
			changeShown: function() {
				this.shown	= [];

				let page	= [1, 0].map(o => ((this.paginateOpts.page - o) * this.paginateOpts.perPage));
				this.$nextTick(() => { this.shown	= this.filtered.slice(page[0], page[1]); });
			},
			init: function() {
				let id	= this.$route.params.id;

				this.paginateOpts.page	= 1;
				this.filterkey			= '';

				axios.get(this.$store.state.baseURL + 'range/' + this.$route.params.id)
					.then(response => {
						this.summary.list.region 	= response.data.regions;
						this.summary.list.years		= response.data.years;

						this.summary.list.start		= JSON.parse(JSON.stringify(response.data.years));
						this.summary.list.end		= JSON.parse(JSON.stringify(response.data.years));

						this.summary.name	= response.data.subject.name;

						_.forEach(this.summary.selected, (o, key) => {
							this.$set(this.summary.selected, key, null);
							this.$refs[key].head();
						});
					})
					.catch(err => { if (err) { console.error(err.response); } })

				axios.get(this.$store.state.baseURL + 'subjects/' + this.$route.params.id)
					.then(response => {
						this.summary.stats	= response.data.summary;
						this.datasets		= response.data.graphs;
					})
					.catch(err => { console.error(err.response); })
			},
		},
		watch: {
			'$route.params.id': function (id) { this.init(); },
			'filterkey': function() { this.paginateOpts.page = 1; },
			'filtered': function(val) { this.changeShown(); },
		},
		components: { Dropdown, D3Map, modalTable, modalMap },
		mounted: function() {
			axios.get(this.$store.state.baseURL + 'subjects')
				.then(response => { this.typeaheadVal = response.data; })
				.catch(err => {  })

			this.init();
		},
		computed: {
			filtered: function() { return this.datasets.filter(o => ( _.includes(o.title.toLowerCase(), this.filterkey.toLowerCase()) )); },
			pageCount: function() { return _.ceil(this.filtered.length / this.paginateOpts.perPage); }
		}
	}
</script>

<style lang="scss">
	@import "~chartist/dist/scss/chartist.scss";
	@import "~chartist-plugin-tooltips/dist/chartist-plugin-tooltip.css";

	$max-width		: 1300px;
	$header-height	: 60px;
	$chart-gap		: 35px;

	$button-clr		: #707070;

	#datapage {
		.wrapper { max-width: $max-width; margin: 0px auto; } position: relative; padding-top: $header-height;
		header {
			background: black; position: fixed; top: 0px; left: 0px; z-index: 28; width: 100vw;
			.wrapper {
				height: $header-height; display: flex; align-items: center;
				div#blurp {
					span {
						font-family: $lato; font-size: 20px; color: white; letter-spacing: -.5px; margin: 0px 10px 0px 5px;
						b { color: firebrick; font-weight: 700; letter-spacing: -.75px; }
					}
					margin-right: 10px;
				}
				.typeahead {
					 flex: 2;  border-bottom: 1px solid #ccc;
					 line-height: 25px; color: white; font-size: 15px;
					 input { background: transparent; border: none; text-align: center; color: white; }
				}
				div#icon-wrapper { margin-left: 10px; text-align: center; }
			}
		}
		section#summary {
			width: 100vw; height: calc(100vh - #{$header-height});
			background-image: url('../assets/data_head.jpg'); background-repeat: no-repeat; background-size: cover;
			#summary-wrapper {
				max-width: 1000px; margin: 0px auto; position: relative; padding-top: 7.5vh; color: black;
				display: flex; flex-direction: column; align-items: center;
				#summary-title {
					margin: auto; padding: 15px 50px;
					text-align: center; font-size: 40px; font-family: $lato; letter-spacing: -1px; text-transform: uppercase;
					border: 3px solid black; border-radius: 5px; margin-bottom: 20px;
				}
				#summary-drops {
					display: grid; grid-template-columns: repeat(2, 200px); grid-column-gap: 50px;
					.drops-wrapper {
						display: flex; flex-wrap: wrap;
						label { width: 100%; text-align: center; color: $magenta; text-transform: lowercase; letter-spacing: -.25px; }
						.placeholder { flex: 2; }
						.divider { width: 50px; text-align: center; color: $magenta; font-size: 16px; font-weight: 700; padding: 10px 0px; }
					}
				}
				#summary-stats {
					display: flex; flex-wrap: wrap; justify-content: space-around; margin-top: 15px; width: 100%;
					.summary-stat-wrapper {
						width: calc((100% / 2) - 5px); text-align: center; margin-top: 25px; display: flex; align-items: center;
						&:nth-child(odd) { margin-right: 10px; }
						.summary-left { flex: 2; text-transform: uppercase; color: $magenta; font-size: 14px; text-align: right; }
						.summary-right {
							width: 40%; margin: 0px 0px 0px 10px;
							.summary-stat-value { font-size: 30px; line-height: 25px; }
							.summary-stat-unit { text-transform: lowercase; font-size: 12px; }
						}
					}
				}
				#summary-another {
					letter-spacing: -.5px; border: 1px solid $magenta; border-radius: 5px; padding: 5px 15px; margin-top: 25px; color: $magenta;
					&.onload { border: none; }
				}
			}
		}
		div.paginate-wrapper {
			position: relative; max-width: $max-width; margin: auto;
			ul.pagination {
				display: flex; justify-content: center; margin: 25px 0px;
				li {
					a { border: 1px solid rgba(black, .2); background: white; padding: 5px 15px; border-radius: 100px; color: $magenta; }
					&:not(:last-child) { margin-right: 7.5px; }
					&.active a { cursor: default; background: $magenta; color: white; border: none; }
					&.disabled a { cursor: not-allowed; color: rgba(black, .2); }
				}
			}
			div.search-wrap {
				position: absolute; top: -7px; right: 0px;
				input { text-align: center; padding: 10px 25px; border-radius: 25px; border: 1px solid rgba(black, .2); width: 200px; }
				svg { position: absolute; top: 10px; right: 10px; }
			}
		}
		section.datasets {
			display: flex; padding: 50px; max-width: calc(#{$max-width} - 100px); margin: auto;
			.detail-wrapper {
				width: 40%; position: relative;
				.detail-title { color: black; font-size: 26px; font-weight: 700; font-family: $lato; letter-spacing: -1px; }
				.detail-year { color: $magenta; font-size: 20px; font-weight: 700; font-family: $lato; letter-spacing: -1px; margin-top: 5px; }
				.detail-desc { margin-top: 10px; text-align: justify; color: darkslategray; }
				.button-wrapper {
					position: absolute; bottom: 10px;
					& > div, & > a {
						display: flex; flex-direction: column; align-items: center; min-width: 75px;
						position: absolute; bottom: 0px;
						.svg-wrapper { border: 1px solid $button-clr; margin-bottom: 5px; display: grid; border-radius: 50%; position: relative; }
						svg { fill: $button-clr; width: 40px; stroke: $button-clr; stroke-width: 0.45px; }
						span { color: $button-clr; font-size: 12px; letter-spacing: -0.5px; }

						// &:not(:last-child) { margin-right: 25px; }
						&:hover {
							svg { fill: $magenta; stroke: $magenta; stroke-width: 1px; }
							span { color: $magenta; font-weight: 700; }
							.svg-wrapper { border-color: $magenta; border-width: 2px; }
						}
					}
				}
			}
			.chart-wrapper { width: 60%; }

			&:nth-child(odd) {
				flex-direction: row-reverse; background: #f5f5f5;
				.detail-wrapper {
					margin-left: $chart-gap;
					.button-wrapper:not(.map) { right: 0px; }
					.button-wrapper.map { right: 75px; }
					.button-wrapper > a { right: 75px; }
					.button-wrapper > div.button-show { right: 0px; }
					.button-wrapper > div.button-map { right: -75px; }
				}
			}
			&:nth-child(even) {
				.detail-wrapper {
					margin-right: $chart-gap;
					.button-wrapper { left: 0px; }
					.button-wrapper > a { left: 0px; }
					.button-wrapper > div.button-show { left: 75px; }
					.button-wrapper > div.button-map { left: 150px; }
				}
			}
		}
		section#nodata { text-align: center; margin: 100px 0px; color: black; }
		footer { height: $header-height; background: black; }
	}
</style>
