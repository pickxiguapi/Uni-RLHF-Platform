<template>
    <v-app>
        <div class="main">
            <transition name="fade">
                <v-alert elevation="5" :type="alertType" style="position: absolute; z-index: 999;" v-if="alertMessage">{{ alertMessage }}</v-alert>
            </transition>
            <div class="topBar">
                <div style="display: flex; align-items: center;">
                    <div class="logo">
                        <img src="@/assets/UniRLHFLogo.jpg" alt="">
                        <p>Uni-RLHF</p>
                    </div>
                    <div style="font-size: 20px; margin-left: 40px;">
                        <p style="display: inline; color: #888888;" @click="back">Projects /</p> {{ taskName }}
                    </div>
                </div>
                <div class="topBar-right">
                    <v-menu offset-y>
                        <template v-slot:activator="{ on, attrs }">
                            <img class="avatar" src="../assets/user.svg" v-bind="attrs" v-on="on">
                        </template>
                        <v-list>
                            <v-list-item @click="logout">
                                <v-icon>mdi-logout</v-icon>
                                <div style="margin-left: 10px;">Log Out</div>
                            </v-list-item>
                            <v-list-item @click="openInNewTab(url_doc)">
                                <v-icon>mdi-file-document-alert-outline</v-icon>
                                <div style="margin-left: 10px;">Docs</div>
                            </v-list-item>
                            <v-list-item @click="openInNewTab(url_github)">
                                <v-icon>mdi-github</v-icon>
                                <div style="margin-left: 10px;">GitHub</div>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                </div>
            </div>

            <div class="infoBar">
                <div>
                    <v-btn class="btn-docs" color="primary" @click="goLabel">Label {{ selected.length == 0 ? "ALL" :
                        selected.length }} Tasks</v-btn>
                    <v-btn v-if="created" class="btn-docs" color="error" @click="deleteTask"
                        style="margin-left: 20px;">Delete Task</v-btn>
                    <v-btn class="btn-docs" color="primary" style="margin-left: 20px;" @click="exportLabel">Export</v-btn>
                    <v-btn class="btn-docs" color="primary" style="margin-left: 20px;"  @click="train">Train</v-btn>
                </div>
                <div class="taskInfo">Task {{ completed }} / {{ total }} &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Annotations:{{
                    annotation }}</div>
            </div>
            <div class="table-div">
                <v-data-table :headers="headers" :items="desserts" v-model="selected" item-key="id" show-select
                    class="table">
                    <template v-slot:header.annotations>
                        <img style="height: 16px;width: 16px;" src="../assets/Annotation.svg">
                    </template>
                    <template v-slot:header.skipped>
                        <img style="height: 16px;width: 16px;" src="../assets/skipped.svg">
                    </template>
                    <template v-slot:item.annotators="{ item }">
                        <div style="display: flex; align-items: center;">
                            <img v-for="i in item.annotators.slice(0, 3)" :src="i" style="height: 22px; margin-right: 5px;">
                        </div>
                    </template>
                    <template v-slot:item.text="{ item }">
                        <div class="text-overflow-ellipsis">
                            {{ item.text }}
                        </div>
                    </template>
                    <template v-slot:item.actions="{ item }">
                        <v-icon color="blue" style="width: 30px;">
                            mdi-xml
                        </v-icon>
                    </template>
                </v-data-table>
            </div>
        </div>
    </v-app>
</template>
<script>
import axios from 'axios';
export default {
    data() {
        return {
            url_doc: '',
            url_github: '',
            alertType:'error',
            alertMessage:'',
            id: '',
            taskName: "",
            created: false,//是自己创建的
            completed: 0,
            total: 0,
            annotation: 0,
            skipped: 0,
            prediction: 0,
            user_id:0,
            selected: [],
            headers: [
                { text: 'ID', align: 'center', sortable: false, value: 'id', },
                { text: 'Completed', value: 'completed', sortable: false, },
                { text: '', align: 'center', value: 'annotations', sortable: false, },
                { text: '', align: 'center', value: 'skipped', sortable: false, },
                { text: 'Annotators', value: 'annotators', sortable: false, },
                { text: 'Label Info', value: 'labelInfo', sortable: false, },
                { text: 'Check', value: 'actions', sortable: false, },
            ],
            desserts: []
        }
    },
    created() {
        this.url_doc = this.$store.state.url_doc
        this.url_github = this.$store.state.url_github
        let id = this.$route.query.id;
        this.id = id
        axios.get(this.$store.state.baseUrl + '/project/' + id + '/' + this.$store.state.username)
            .then((response) => {
                console.log(response)
                let info = response.data.project
                this.completed = info.annotation_num //
                this.total = info.query_num
                this.annotation = info.annotation_num
                this.taskName = info.project_name
                this.created = response.data.deletable == 1
                this.user_id = response.data.user_id
                this.feedback_type = info.feedback_type

                axios.get(this.$store.state.baseUrl + '/query/' + id)
                    .then((res) => {
                        let querys = res.data.querys
                        console.log(querys)
                        
                        for (let i = 0; i < querys.length; i++) {
                            let item = {}
                            item.id = querys[i].query_id
                            item.completed = this.formatDateTime(querys[i].completion_time)
                            item.annotations = querys[i].marked_num
                            item.skipped = querys[i].skip_num
                            item.text = querys[i].label
                            let annotators_arr = []
                            
                            for(let j=0;j<querys[i].annotators.length;j++){
                                annotators_arr.push("https://ui-avatars.com/api/?name="+ querys[i].annotators[i] +"&background=random&rounded=true")
                            }
                            item.annotators = annotators_arr
                            item.labelInfo = querys[i].label_info
                            
                            this.desserts.push(item)
                        }
                    })
                    .catch(() => {

                    })
            })
            .catch((error) => {
                console.error('error:', error);
            });
    },
    methods: {
        logout() {
            this.$store.commit('setUsername', '');
            this.$store.commit('setRole', '');
            this.$store.commit('setPassword', '');
            this.$store.commit('setEmail', '');
            this.$router.push('/')
        },
        back() {
            this.$router.push("/homepage")
        },
        goLabel() {
            let list = []
            if(this.selected.length == 0){
                for(let i=0;i<this.desserts.length;i++){
                    list.push(this.desserts[i].id)
                }
            }else{
                for(let i=0;i<this.selected.length;i++){
                    list.push(this.selected[i].id)
                }
            }
            this.$router.push({
                name: this.feedback_type,
                query: {
                    user_id: this.user_id,
                    query_id_list: list,
                    taskName: this.taskName,
                    taskID: this.id
                }
            });
        },
        deleteTask() {
            let id = this.$route.query.id;
            axios.get(this.$store.state.baseUrl + '/delete_project/' + id + '/' + this.$store.state.username)
                .then((response) => {
                    console.log(response.data)
                    this.alertV("Task deleted successfully",'success')
                    this.$router.push("/Homepage")
                })
                .catch((error) => {
                    console.error('error:', error);
                });
        },
        formatDateTime(inputDate) {
            if(inputDate == null){
                return ''
            }
            const months = [
                'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
            ];
            // 辅助函数：将数字转换为两位数的字符串
            function padZero(num) {
                return num.toString().padStart(2, '0');
            }
            // 解析原始日期字符串
            const parsedDate = new Date(inputDate);
            // 获取年、月、日、时、分
            const year = parsedDate.getFullYear();
            const month = months[parsedDate.getMonth()];
            const day = parsedDate.getDate();
            const hours = parsedDate.getHours();
            const minutes = parsedDate.getMinutes();
            // 格式化为 "yyyy/mm/dd hh:mm" 格式
            const formattedDate = `${year}/${padZero(parsedDate.getMonth() + 1)}/${padZero(day)} ${padZero(hours)}:${padZero(minutes)}`;
            return formattedDate;
        },
        exportLabel(){
            let id = this.$route.query.id;
            window.open(this.$store.state.baseUrl + '/export_label/' + id, '_blank');

            // axios.get(this.$store.state.baseUrl + '/export_label/' + id )
            //     .then((response) => {

            //     })
            //     .catch((error) => {
            //         console.error('error:', error);
            //     });
        },
        train(){

        },
        openInNewTab(url) {
            window.open(url, '_blank');
        },
        alertV(message,type){
            this.alertType = type
            this.alertMessage = message
            setTimeout(()=>{
                this.alertType = ''
                this.alertMessage = ''
            },4000)
        }
    }
}
</script>
<style scoped>
.main {
    background-color: #f9f9f9;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between
}

.topBar {
    z-index: 100;
    position: fixed;
    background-color: #fff;
    width: 100vw;
    height: 48px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0px 1px 10px 0px rgba(0, 0, 0, 0.2);
}

.logo {
    height: 36px;
    width: 160px;
    margin-left: 24px;
    line-height: 36px;
    display: flex;
    justify-content: center;
    color: #333333;
    font-size: 22px;
    font-weight: 900;
}


.topBar-right {
    height: 36px;
    margin-right: 24px;
    display: flex;
    align-items: center;
}

.btn-docs {
    margin-right: 0%;
}

.avatar {
    height: 30px;
    width: 30px;
    margin-left: 24px;
}

.infoBar {
    position: fixed;
    top: 48px;
    height: 40px;
    width: 100vw;
    background-color: #f3f3f3;
    z-index: 100;
    padding: 0px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.taskInfo {
    color: rgba(0, 0, 0, 0.6);
}

.table-div {
    margin-top: 88px;
    height: calc(100vh - 88px);
    width: 100vw;
}

.table {
    height: calc(100vh - 88px);
    width: 100vw;
}

.text-overflow-ellipsis {
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
    width: 15vw;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>