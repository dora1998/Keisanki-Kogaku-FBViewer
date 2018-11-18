Vue.component('fb-list', {
    template: '#fb-list',
    props: ['fb_date'],
    data: function () {
        return {
            lessons: []
        }
    },
    mounted: function() {
        var vue_obj = this
        fetch("./data/fb.json")
            .then(function(response) {
                return response.json()
            })
            .then(function(jsondata) {
                vue_obj.lessons = jsondata
                vue_obj.changeFb(vue_obj.lessons[0])
            });
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

new Vue({
    el: "#parent",
    data() {
        return {
            fb_date: ""
        }
    },
    methods: {
        changeFb(value) {
            this.fb_date = value
        }
    }
  });