<template lang="html">
	<div id="homepage">
		<section id="header">
			<div id="wrapper" class="noselect">
				<div id="logo"><span>dataku</span><b>ID</b></div>
				<!-- <div id="bullshit">A wonderful serenity has taken possession of my entire soul, like these sweet mornings of spring which I enjoy with my whole heart.</div> -->
				<div id="search">
					<vue-single-select @input="onCateClick" v-model="search" :options="typeaheadVal" optionLabel="name" class="typeahead" placeholder="Cari berdasarkan tema (min. 3 karakter)"></vue-single-select>
					<div id="icon-wrapper"><font-awesome-icon icon="search" /></div>
				</div>
			</div>
		</section>
	</div>
</template>

<script>
	import axios from 'axios'

	export default {
		name: 'Home',
		data: () => ({
			search: '',
			typeaheadVal: [],
		}),
		methods: {
			componentName: function(o) { return 'featured_' + o.id; },
			onCateClick: function(o) { if (o.id) { this.$nextTick(() => { this.$router.push({ name: 'data', params: { id: o.id } }) }) } },
		},
		mounted: function() {
			axios.get(this.$store.state.baseURL + 'subjects')
				.then(response => { this.typeaheadVal = response.data; })
				.catch(err => {  })
		}
	}
</script>

<style lang="scss">
	$search-height	: 50px;

	#homepage {
		background: black;
		section#header {
			width: 100vw; height: 100vh; position: relative;
			background-image: url('../assets/header.jpg'); background-repeat: no-repeat; background-size: cover;
			#wrapper {
				max-width: 600px; margin: 0px auto; position: relative; padding-top: 25vh;
				#logo {
					text-align: center; font-family: $lato; font-size: 80px; margin-bottom: 25px;
					span { color: white; letter-spacing: -5px; }
					b { color: firebrick; font-weight: 700; letter-spacing: -7.5px; }
				}
				#bullshit { text-align: center; margin: 10px 30px 15px; }
				#search {
					width: 100%; display: flex; line-height: $search-height;
					input { flex: 2; border: none; text-align: center;}
					div#icon-wrapper { width: 60px; text-align: center; background: $magenta; }
					.typeahead {
						flex: 2; border: none; text-align: center; background: white; color: black; padding: 0px;
						input { line-height: $search-height; }
						ul {
							li { padding: 15px 20px; &.active { background: $magenta; color: white; } }
						}
					}
				}
			}
			#scroll {
				font-family: $lato; font-weight: bolder; text-transform: lowercase; letter-spacing: -.5px; font-size: 16px; width: 100%; text-align: center;
				position: absolute; bottom: 20px;
			}
		}
	}
</style>
