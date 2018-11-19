Vue.component('fb-list', {
    template: '#fb-list',
    props: ['lessons', 'fb_date'],
    data: function () {
        return {}
    },
    watch: {
        lessons() {
            this.changeFb(this.lessons[0])
        }
    },
    methods: {
        changeFb(value) {
            this.$emit('change-fb', value)
        }
    }
})

Vue.component('fb-body', {
    template: '#fb-body',
    data: function () {
        return {
            fbdata: {}
        }
    },
    props: ['fb_date'],
    watch: {
        fb_date: function() {
            var vue_obj = this
            fetch("./data/" + this.fb_date + ".json")
                .then(function(response) {
                    return response.json()
                })
                .then(function(jsondata) {
                    jsondata.ans.forEach(function(value, index, array) {
                        array[index].ans = JSON.parse(value.ans.replace(/\'/g, '"'))
                    })
                    vue_obj.fbdata = jsondata
                });
        }
    }
})

Vue.component('graph-rate', {
    extends: VueChartJs.HorizontalBar,
    data: function () {
        return {
            colorTrue: '#f87979',
            colorFalse: '#3e79e0',
            option: {
                responsive: true, 
                maintainAspectRatio: false,
                scales: {
                    xAxes: [{
                        ticks: {
                            beginAtZero: true,
                            min: 0
                        }
                    }]
                },
            },
        }
    },
    props: ['ans', 'stats'],
    computed: {
        labels() {
            var res = []
            for (let i of this.stats) {
                res.push(i.qname)
            }
            return res
        },
        datasets() {
            var bg = []
            for (let i of this.ans) {
                bg.push(i.res == 'True' ? this.colorTrue : this.colorFalse)
            }
            var graphData = []
            for (let i of this.stats) {
                graphData.push(i.rate)
            }
            return [{
                label: '正答率',
                backgroundColor: bg,
                data: graphData
            }]
        },
    },
    mounted () {
        this.renderChart({
            labels: this.labels,
            datasets: this.datasets
        }, this.option)
    },
    watch: {
        ans() {
            this.renderChart({
                labels: this.labels,
                datasets: this.datasets
            }, this.option)
        },
        stats() {
            this.renderChart({
                labels: this.labels,
                datasets: this.datasets
            }, this.option)
        }
    }
})

Vue.component('graph-score', {
    extends: VueChartJs.HorizontalBar,
    data: function () {
        return {
            option: {
                responsive: true, 
                maintainAspectRatio: false,
                scales: {
                    xAxes: [{
                        ticks: {
                            beginAtZero: true,
                            min: 0
                        }
                    }]
                },
            },
        }
    },
    props: ['stats'],
    computed: {
        labels() {
            var res = []
            for (let key in this.stats) {
                res.push(Number(key))
            }
            return res
        },
        datasets() {
            var graphData = []
            for (let key in this.stats) {
                graphData.push(Number(this.stats[key]))
            }
            return [{
                label: '人数分布',
                backgroundColor: '#88cd8d',
                data: graphData
            }]
        },
    },
    mounted () {
        this.renderChart({
            labels: this.labels,
            datasets: this.datasets
        }, this.option)
    },
    watch: {
        ans() {
            this.renderChart({
                labels: this.labels,
                datasets: this.datasets
            }, this.option)
        },
        stats() {
            this.renderChart({
                labels: this.labels,
                datasets: this.datasets
            }, this.option)
        }
    }
})

Vue.component('graph-history', {
    extends: VueChartJs.Bar,
    data: function () {
        return {
            graphData: [],
            labels: [],
            option: {
                responsive: true, 
                maintainAspectRatio: false,
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true,
                        }
                    }]
                },
            },
        }
    },
    props: ['lessons'],
    computed: {
        datasets() {
            avgArr = []
            for (let i = 0; i < this.graphData.length; i++) {
                avgArr.push(this.avg)
            }
            return [
            {
                label: '成績',
                backgroundColor: '#88cd8d',
                data: this.graphData
            },
            {
                label: '平均点',
                borderColor: '#ff0000',
                borderWidth: 2,
                pointRadius: 0,
				fill: false,
                data: avgArr,
                type: 'line'
            }]
        },
        avg() {
            let sum = 0
            let count = 0
            for (let i of this.graphData) {
                count += 1
                sum += i
            }
            return sum / count
        }
    },
    mounted () {
        this.getAllFeedback()
    },
    watch: {
        lessons() {
            this.getAllFeedback()
        },
        datasets() {
            this.renderChart({
                labels: this.labels,
                datasets: this.datasets
            }, this.option)
        }
    },
    methods: {
        getAllFeedback() {
            for (const l of this.lessons) {
                var $vm = this
                fetch("./data/" + l + ".json")
                    .then(function(response) {
                        return response.json()
                    })
                    .then(function(jsondata) {
                        jsondata.ans.forEach(function(value, index, array) {
                            array[index].ans = JSON.parse(value.ans.replace(/\'/g, '"'))
                        })
                        
                        let sumQ = 0
                        let trueQ = 0
                        for (let a in jsondata.ans) {
                            sumQ += 1
                            if (jsondata.ans[a].res == 'True') {
                                trueQ += 1
                            }
                        }
                        $vm.labels.push(l)
                        $vm.graphData.push(trueQ / sumQ * 100)
                    });
            }
        },
    }
})

new Vue({
    el: "#parent",
    data() {
        return {
            fb_date: "",
            lessons: []
        }
    },
    mounted: function() {
        var $vm = this
        fetch("./data/fb.json")
            .then(function(response) {
                return response.json()
            })
            .then(function(jsondata) {
                $vm.lessons = jsondata
            });
    },
    methods: {
        changeFb(value) {
            this.fb_date = value
        }
    }
  });