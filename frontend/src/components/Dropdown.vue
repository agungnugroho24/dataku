<template lang="html">
	<div class="dropdown" ref="target">
		<div class="selected">
			<span>{{ selected }}</span>
			<font-awesome-icon icon="caret-down" />
		</div>
		<ul :class="{ hidden: !isopen }">
			<li v-for="o in droplist" @click="onselect(o)">{{ o.val }}</li>
		</ul>
	</div>
</template>

<script>
	export default {
		name: 'Dropdown',
		props: ['list', 'pickLast'],
		data: () => ({
			isopen: false,
			selected: '',
			droplist: [],
		}),
		methods: {
			onclick: function(e) {
				let el		= this.$refs.target;
				let target	= e.target;

				if (( el !== target) && !el.contains(target)) {
					this.isopen = false;
				} else { this.isopen = !this.isopen; }
			},
			onselect: function(o) {
				if (o.val !== this.selected) {
					this.selected = o.val;
					this.$emit('dropchange', o);
				}
			},
			head: function() { this.selected = _.chain(this.droplist).head().get('val').value(); }
		},
		watch: {
			list: { immediate: true, handler (val, oldVal) {
					let array	= _.chain(val).toPairs().map(o => ({ id: o[0], val: o[1] })).orderBy(['id'], [(_.isNil(this.pickLast) ? 'asc' : 'desc')]).value();

					if (_.isEmpty(this.selected)) { this.selected = _.chain(array).head().get('val').value(); }
					this.droplist	= array;

					// this.$emit('')
				}
			}
		},
		mounted: function() {
			window.addEventListener('click', this.onclick);
		},
		destroyed: function() {
			window.removeEventListener('click', this.onclick);
		}
	}
</script>

<style lang="scss">
	.dropdown {
		text-align: center; position: relative; border-bottom: 1px solid black; padding: 10px 0px;
		.selected {
			svg { position: absolute; right: 5px; bottom: 17.5px; }
		}
		ul {
			position: absolute; top: 50px; left: 0px; width: 100%; background: white; border: 1px solid #eee; border-radius: 5px; max-height: 300px; overflow-y: auto;
			li { padding: 10px 0px; &:not(:last-child) { border-bottom: 1px solid #ccc; } &:hover { background: $magenta; color: white; } }
		}
	}
</style>
