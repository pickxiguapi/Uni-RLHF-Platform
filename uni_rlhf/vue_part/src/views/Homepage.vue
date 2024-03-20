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
                        <p style="display: inline;">Projects</p>
                    </div>
                </div>
                <!-- <v-btn class="btn-docs" color="primary" @click="labelAll">Label All Tasks</v-btn> -->
                <div class="topBar-right">
                    <v-text-field v-model="TaskID" outlined dense label="Bind Task By ID" append-icon="mdi-link-variant"
                        style="transform: translateY(13px); margin-right: 30px;" @click:append="BindByID"></v-text-field>
                    <v-btn class="btn-docs" color="primary" @click="createTaskPop">Create</v-btn>
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
            <div class="currentTask">
                <div class="title">Current Project</div>
                <div class="currentTaskMain">
                    <div class="content-empty" v-if="empty1">
                        <p style="font-size: 48px; font-weight: 600;">Nothing here!</p>
                    </div>
                    <div class="content" v-if="currentTask !== undefined && currentTask != null && currentTask.length > 0">
                        <div v-for="task in currentTask" class="taskCard"
                            @click="task.status == 'activation' ? goTaskCurrent(task) : null" style="position: relative;">
                            <div class="creatingMask" v-if="task.status != 'activation'">
                                <v-progress-circular indeterminate color="blue" :size="50"></v-progress-circular>
                            </div>
                            <div class="cardTitle">
                                <p>{{ task.title }}</p>
                                <div>
                                    <v-menu offset-y open-on-hover>
                                        <template v-slot:activator="{ on, attrs }">
                                            <v-icon v-bind="attrs" v-on="on">mdi-dots-horizontal</v-icon>
                                        </template>
                                        <v-list>
                                            <v-list-item @click="openView(task.id)">
                                                <v-icon>mdi-store-search-outline</v-icon>
                                                <div style="margin-left: 10px;">View</div>
                                            </v-list-item>
                                        </v-list>
                                    </v-menu>
                                </div>
                            </div>
                            <div class="cardEnv">
                                <p>{{ task.env }}</p>
                            </div>
                            <div class="cardNumber">
                                <div>{{ task.completed }} / {{ task.total }}</div>
                                <div style="display: flex; align-items: center;">
                                    <img src="../assets/Annotation.svg">
                                    <div style="margin-left: 1px;">{{ task.annotation }}</div>
                                    <img style="margin-left: 10px;" src="../assets/skipped.svg">
                                    <div style="margin-left: 1px;">{{ task.skipped }}</div>
                                </div>
                            </div>
                            <div style="height: 10px;">
                            </div>
                            <div class="cardBottom">
                                <div style="font-size: 14px; color: rgba(0,0,0,0.5)">{{ task.date }}</div>
                                <div>
                                    <img v-for="i in task.avatar.slice(0, 3)" style="margin-left: 5px;" :src=i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="taskPool">
                <div class="title">Project Pool</div>
                <div class="taskPoolMain">
                    <div class="content-empty" v-if="empty2">
                        <p style="font-size: 48px; font-weight: 600;">Nothing here!</p>
                    </div>
                    <div class="content" v-if="taskPool !== undefined && taskPool != null && taskPool.length > 0">
                        <!-- <div v-for="task in taskPool" class="taskCard"  @click="goTaskPool(task)"> -->
                        <div v-for="task in taskPool" class="taskCard" style="position: relative;">
                            <div class="creatingMask" v-if="task.status != 'activation'">
                                <v-progress-circular indeterminate color="blue" :size="50"></v-progress-circular>
                            </div>
                            <div class="cardTitle">
                                <p>{{ task.title }}</p>
                                <div>
                                    <v-menu offset-y open-on-hover>
                                        <template v-slot:activator="{ on, attrs }">
                                            <v-icon v-bind="attrs" v-on="on">mdi-dots-horizontal</v-icon>
                                        </template>
                                        <v-list>
                                            <v-list-item @click="task.status == 'activation' ? takeTask(task.id) : null">
                                                <v-icon>mdi-link-variant</v-icon>
                                                <div style="margin-left: 10px;">Bind</div>
                                            </v-list-item>
                                            <v-list-item @click="openView(task.id)">
                                                <v-icon>mdi-store-search-outline</v-icon>
                                                <div style="margin-left: 10px;">View</div>
                                            </v-list-item>
                                        </v-list>
                                    </v-menu>
                                </div>
                            </div>
                            <div class="cardEnv">
                                <p>{{ task.env }}</p>
                            </div>
                            <div class="cardNumber">
                                <div>{{ task.completed }} / {{ task.total }}</div>
                                <div style="display: flex; align-items: center;">
                                    <img src="../assets/Annotation.svg">
                                    <div style="margin-left: 1px;">{{ task.annotation }}</div>
                                    <img style="margin-left: 10px;" src="../assets/skipped.svg">
                                    <div style="margin-left: 1px;">{{ task.skipped }}</div>
                                </div>
                            </div>
                            <div style="height: 10px;">
                            </div>
                            <div class="cardBottom">
                                <div style="font-size: 14px; color: rgba(0,0,0,0.5)">{{ task.date }}</div>
                                <div>
                                    <img v-for="i in task.avatar.slice(0, 3)" style="margin-left: 5px;" :src=i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <!-- 创建任务 -->
            <v-dialog v-model="dialog" width="1000">
                <v-card>
                    <v-toolbar flat color="white">
                        <v-toolbar-title>Create Project</v-toolbar-title>
                        <v-spacer></v-spacer>
                        <v-btn @click="closePop" outlined color="error">
                            Delete
                        </v-btn>
                        <v-btn style="margin-left: 15px;" @click="createTask" color="primary">
                            Create
                        </v-btn>
                    </v-toolbar>
                    <!-- <v-tabs color="blue accent-4" centered style="border-radius: 24px; height: 300px;"> -->
                    <!-- <v-tab style="text-transform: none !important;">Feedback</v-tab> -->
                    <!-- <v-tab style="text-transform: none !important;">Setting</v-tab> -->
                    <!-- <v-tab-item> -->
                    <!-- <div class="LabelSetup">
                                <div v-for="(item, index) in feedbacks" :key="item.type"
                                    @click="selectFeedback(index, item)"
                                    :class="(index == Feedback_Select) ? 'feedbackItem_activate' : 'feedbackItem'">
                                    <img :src=item.img class="feedbackImg">
                                    <div class="feedbackTitle">
                                        <p>{{ item.type }}</p>
                                    </div>
                                </div>
                            </div> -->
                    <!-- </v-tab-item> -->
                    <!-- <v-tab-item> -->
                    <v-form ref="createForm" class="projectName" lazy-validation>
                        <v-text-field class="createInput" v-model="ProjectName" dense label="Project Name" outlined
                            color="blue" :rules="ProjectNameRules"></v-text-field>
                        <v-textarea v-model="Description" class="createInput" label="Description" outlined rows="3"
                            hint="Enter the project description (optional)"></v-textarea>
                        <div class="createInput" style="height: 20px; ">
                            <p style="line-height: 20px;font-size: 14 px;">Due time:</p>
                        </div>
                        <input style="margin-bottom: 25px;" class="createInputTime" v-model="dueTime" type="datetime-local"
                            value="2023-12-31T00:00">
                        <div class="createInput" style="height: 20px;">
                            <p style="line-height: 20px;font-size: 14 px;">Sampler Type:</p>
                        </div>
                        <v-radio-group v-model="SamplerType" row style="width: 80%;margin-top: 0;">
                            <v-radio v-for="item in config.sampler_type" :label="item" :value="item"></v-radio>
                        </v-radio-group>

                        <div class="createInput" style="height: 20px;">
                            <p style="line-height: 20px;font-size: 14 px;">FeedBack Type:</p>
                        </div>
                        <v-radio-group v-model="FeedbackType" row style="width: 80%;margin-top: 0;">
                            <v-radio v-for="item in config.feedback_type" :label="item" :value="item"></v-radio>
                        </v-radio-group>

                        <div class="createInput" style="height: 20px;">
                            <p style="line-height: 20px;font-size: 14 px;">Mode:</p>
                        </div>
                        <v-radio-group v-model="Mode" class="createInput" row style="margin-top: 0;">
                            <v-radio v-for="item in config.mode" :label="item" :value="item"></v-radio>
                        </v-radio-group>

                        <div class="createInput" style="height: 20px;">
                            <p style="line-height: 20px;font-size: 14 px;">Instruction:</p>
                        </div>
                        <wang-editor v-model="Instruction" class="createInput" style="margin-bottom: 20px;z-index:100" />

                        <div style="width: 80%;">
                            <v-text-field v-model="addQuestion" outlined dense label="Add Question"
                                prepend-icon="mdi-plus-circle" @click:prepend="addAQuestion"
                                style="margin-bottom: 0;"></v-text-field>
                            <div v-for="(item, index) in Question"
                                style="outline: solid 1px;outline-color: #9f9f9f; border-radius: 5px; padding: 10px; width: 100%;margin-bottom: 10px;">
                                <div
                                    style="width: 100%;height:20px;display: flex;justify-content: space-between;margin-bottom: 20px;">
                                    <div style="line-height: 20px;font-size: 16px;">Qustion{{
                                        index
                                        + 1 }}: {{ item }}</div>
                                    <v-icon style="width: 20px;height: 20px;"
                                        @click="delQuestion(index)">mdi-delete-forever-outline</v-icon>
                                </div>

                                <div class="createInput" style="height: 20px;">
                                    <p style="line-height: 20px;font-size: 14px;">Option Type:</p>
                                </div>
                                <v-radio-group v-model="QustionOptionType[index]" row style="width: 80%; margin-top: 0;">
                                    <v-radio label="SingleChoice" value="SingleChoice"></v-radio>
                                    <v-radio label="MultipleChoice" value="MultipleChoice" disabled></v-radio>
                                </v-radio-group>
                                <v-text-field v-model="QuestionAddOption[index]" outlined dense label="Add Option"
                                    prepend-icon="mdi-plus-circle" @click:prepend="addAQuestionOption(index)"
                                    style="margin-bottom: 0;"></v-text-field>
                                <div style="height: 30px;" v-if="QuestionOptions[index].length != 0">
                                    <p style="line-height: 30px;font-size: 14 px;">Options:</p>
                                </div>
                                <v-chip v-for="(op, i) in QuestionOptions[index]" color="primary lighten-1" close
                                    @click:close="delOption(index, i)" style="margin: 5px 1%;">{{ op }}</v-chip>
                            </div>
                        </div>


                        <div class="createInput" style="height: 20px;margin-top: 10px;">
                            <p style="line-height: 20px;font-size: 14 px;">Dataset Type:</p>
                        </div>
                        <v-radio-group v-model="DatasetType" row style="width: 80%; margin-top: 0;">
                            <v-radio label="Existed" value="Existed"></v-radio>
                            <v-radio label="Upload" value="Upload"></v-radio>
                        </v-radio-group>
                        <cas :data="config.exsited_datasets" @on-change="handleChange" class="createInput"
                            v-if="DatasetType === 'Existed'">
                            <v-combobox label="Dataset" dense outlined v-model="selected_dataset" readonly
                                :rules="SelectedDatasetRules"></v-combobox>
                        </cas>
                        <v-file-input class="createInput" label="Upload Files" v-if="DatasetType === 'Upload'"
                            prepend-icon="mdi-file-upload-outline" accept=".h5, .hdf5" @change="validateFile"
                            ref="fileInput" outlined dense :rules="SelectedDatasetRules"></v-file-input>
                        <div style="width: 80%; display: flex; justify-content: space-between;">
                            <v-text-field class="createInput" style="margin-right: 30px;" v-model="QueryNum" dense
                                label="Query Number" outlined color="blue" type="number"
                                :rules="queryNumRules"></v-text-field>
                            <v-text-field class="createInput" v-model="QueryLength" dense label="Query Length" outlined
                                color="blue" type="number" :rules="queryLengthRules"></v-text-field>
                        </div>
                        <div style="width: 80%; display: flex; justify-content: space-between;">
                            <v-text-field class="createInput" style="margin-right: 30px;" v-model="VideoWidth" dense
                                label="Video Width" outlined color="blue" type="number"
                                :rules="VideoWidthRules"></v-text-field>
                            <v-text-field class="createInput" v-model="VideoHeight" dense label="Video Height" outlined
                                color="blue" type="number" :rules="VideoHeightRules"></v-text-field>
                        </div>
                        <v-slider label="fps" class="createInput" style="margin-top: 20px;" :max="config.fps.maximum"
                            :min="config.fps.minimum" v-model="fps" thumb-label="always"></v-slider>

                        <!-- options -->
                        <div style="width: 80%;">
                            <v-text-field v-model="addTag" outlined dense label="Add Tag" prepend-icon="mdi-plus-circle"
                                @click:prepend="addATag"></v-text-field>
                            <div style="height: 30px;" v-if="Tag.length != 0">
                                <p style="line-height: 30px;font-size: 14 px;">Tags:</p>
                            </div>
                            <div style="height: auto; margin-bottom: 20px;">
                                <v-chip v-for="(item, index) in Tag" color="primary lighten-1" close
                                    @click:close="delTag(index)" style="margin: 5px 1%;">{{ item }}</v-chip>
                            </div>
                        </div>
                        <v-switch class="createInput" style="margin-top: 0;" v-model="visibility" inset
                            :label="`Visibility: ${visibility ? 'public' : 'private'}`"></v-switch>
                    </v-form>
                    <!-- </v-tab-item> -->
                    <!-- </v-tabs> -->

                </v-card>
            </v-dialog>
            <!-- view -->
            <v-dialog v-model="viewDialog" width="700">
                <v-card>
                    <v-toolbar flat color="white">
                        <v-toolbar-title>View</v-toolbar-title>
                        <v-spacer></v-spacer>
                        <v-icon @click="closeView">mdi-close</v-icon>
                    </v-toolbar>
                    <div style="padding-bottom: 20px;width: 100%;" class="projectName">
                        <div v-for="(value, key, index) in view" class="view_item">
                            <v-textarea style="width: 100%;resize: none" dense :label="String(key)" :value="String(value)"
                                outlined readonly color="blue" auto-grow rows="1"></v-textarea>
                        </div>
                    </div>
                </v-card>
            </v-dialog>
        </div>
    </v-app>
</template>
<script>
import axios from 'axios';
import { Cascader } from "iview";
import WangEditor from '../components/wangEditor.vue';

export default {
    components: {
        cas: Cascader,
        WangEditor
    },
    data() {
        return {
            url_doc: '',
            url_github: '',
            alertType:'error',
            alertMessage:'',
            colors: [
                'primary',
                'secondary',
                'yellow darken-2',
                'red',
                'orange',
            ],
            feedbacks: [{ type: "Comparative", img: require("@/assets/feedback/Comparative.png") },
            { type: "Evaluative", img: require("@/assets/feedback/Evaluative.png") },
            { type: "Keypoint", img: require("@/assets/feedback/Keypoint.png") },
            { type: "Visual", img: require("@/assets/feedback/Visual.png") },
            { type: "Attribute", img: require("@/assets/feedback/Attribute.png") },
            ],
            view: {},
            dialog: false,
            viewDialog: false,
            empty: false,
            //使用id绑定任务
            TaskID: '',
            //创建任务字段
            FeedbackType: "",
            Feedback_Select: 0,
            dataset_path: "",
            file: '',
            ProjectName: "",
            ProjectNameRules: [v => !!v || 'Cannot be empty'],
            dueTime: "",
            DatasetType: 'Existed',
            selected_dataset: '',
            SelectedDatasetRules: [v => !!v || 'Cannot be empty'],
            Domain: -1,  //domian id
            Task: -1,  //任务id
            Environment: -1, //环境id
            QueryNum: 0,
            fps: 20,//根据task变化
            QueryLength: 0,
            Description: "",
            Instruction: ``,
            addQuestion: '',
            Question: [],
            QustionOptionType: [],
            QuestionAddOption: [],
            QuestionOptions: [],
            visibility: true,
            Mode: "",
            SamplerType: "",
            addTag: "",
            Tag: [],
            VideoWidth: 0,
            VideoHeight: 0,
            queryNumRules: [],
            queryLengthRules: [],
            VideoWidthRules: [],
            VideoHeightRules: [],

            //
            currentTask: [],
            taskPool: [],
            empty1: false,
            empty2: false,

            //
            config: {
                "sampler_type": ["Random", "Disagreement", "Schedule"],
                "feedback_type": ["Comparative", "Attribute", "Evaluative", "Visual", "Keypoint"],
                "mode": ["Offline", "Online"],
                "dataset_type": ["Existed", "Upload"],
                "exsited_datasets": [
                    {
                        "label": "D4RL",
                        "value": 1,
                        "children": [
                            {
                                "label": "mujoco",
                                "value": 11,
                                "children": [
                                    {
                                        "label": "walker2d-medium-v2",
                                        "value": 1101
                                    },
                                    {
                                        "label": "walker2d-medium-replay-v2",
                                        "value": 1102
                                    },
                                    {
                                        "label": "walker2d-medium-expert-v2",
                                        "value": 1103
                                    },
                                    {
                                        "label": "walker2d-expert-v2",
                                        "value": 1104
                                    },
                                    {
                                        "label": "hopper-medium-v2",
                                        "value": 1105
                                    },
                                    {
                                        "label": "hopper-medium-replay-v2",
                                        "value": 1106
                                    },
                                    {
                                        "label": "hopper-medium-expert-v2",
                                        "value": 1107
                                    },
                                    {
                                        "label": "hopper-expert-v2",
                                        "value": 1108
                                    },
                                    {
                                        "label": "halfcheetah-medium-v2",
                                        "value": 1109
                                    },
                                    {
                                        "label": "halfcheetah-medium-replay-v2",
                                        "value": 1210
                                    },
                                    {
                                        "label": "halfcheetah-medium-expert-v2",
                                        "value": 1211
                                    },
                                    {
                                        "label": "halfcheetah-expert-v2",
                                        "value": 1212
                                    }
                                ]
                            },
                            {
                                "label": "antmaze",
                                "value": 12
                            },
                            {
                                "label": "adroit",
                                "value": 13
                            }
                        ]
                    },
                    {
                        "label": "Atari",
                        "value": 2
                    },
                    {
                        "label": "SMARTS",
                        "value": 3
                    }
                ],
                "query_num": {
                    "type": "integer",
                    "default": 20,
                    "minimum": 1,
                    "maximum": 500
                },
                "query_length": {
                    "type": "integer",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 999
                },
                "video_width": {
                    "type": "integer",
                    "default": 500,
                    "minimum": 84,
                    "maximum": 500
                },
                "video_height": {
                    "type": "integer",
                    "default": 500,
                    "minimum": 84,
                    "maximum": 500
                },
                "fps": {
                    "type": "integer",
                    "default": 25,
                    "minimum": 1,
                    "maximum": 50
                }
            }

        }
    },
    computed: {
        isValidInvisibleQuestion() {
            let a = this.Question.length > 0;
            let b = 0
            for (let i = 0; i < this.Question.length; i++) {
                if (this.QuestionOptions[i].length > 0) {
                    b++;
                }
            }
            return (a && (b === this.Question.length))
        }
    },
    created() {
        this.url_doc = this.$store.state.url_doc
        this.url_github = this.$store.state.url_github
        let currentDate = new Date();
        currentDate.setDate(currentDate.getDate() + 7);
        this.dueTime = currentDate.toISOString().substring(0, 16);
        this.empty1 = false
        this.empty2 = false
        axios.get(this.$store.state.baseUrl + '/get_default_json')
            .then((r) => {
                this.config = r.data
                this.closePop()
            })
            .catch((error)=>{

            })

        axios.post(this.$store.state.baseUrl + '/projects/' + this.$store.state.username)
            .then((response) => {
                // console.log(response.data)
                this.currentTask = this.transformTasks(response.data.currentprojects)
                this.taskPool = this.transformTasks(response.data.projects)
                console.log("current", this.currentTask)
                if (this.currentTask == undefined || this.currentTask == null || this.currentTask.length <= 0) {
                    this.empty1 = true
                }
                if (this.taskPool == undefined || this.taskPool == null || this.taskPool.length <= 0) {
                    this.empty2 = true
                }

            })
            .catch((error) => {
                console.error('error:', error);
                if (this.currentTask == undefined || this.currentTask == null || this.currentTask.length <= 0) {
                    this.empty1 = true
                }
                if (this.taskPool == undefined || this.taskPool == null || this.taskPool.length <= 0) {
                    this.empty2 = true
                }
            });
    },

    methods: {
        transformTasks(responseData) {
            return responseData.map((task) => {
                let avatars = []
                for (let i = 0; i < task.associated_usernames.length; i++) {
                    avatars.push("https://ui-avatars.com/api/?length=3&name=" + task.associated_usernames[i] + "&background=random&rounded=true")

                }
                return {
                    id: task.project_id,
                    title: task.project_name,
                    env: task.environment_name,
                    completed: task.annotation_num,
                    total: task.query_num,
                    annotation: task.annotation_num,
                    status: task.status,
                    skipped: task.skip_num,
                    date: new Date(task.create_time).toLocaleString(),
                    avatar: avatars
                };
            });
        },
        async uploadFile() {
            console.log(this.file)
            if (!this.file) {
                return ""
            }
            const formData = new FormData();
            formData.append('file', this.file);
            console.log(formData)
            axios.post(this.$store.state.baseUrl + '/upload_hdf5', formData)
                .then((response) => {
                    // this.alertV(response.data.message,'success')
                })
                .catch((error) => {
                    // this.alertV(error.response.data.message,'error')
                })
        },
        logout() {
            this.$store.commit('setUsername', '');
            // this.$store.commit('setRole', '');
            this.$store.commit('setPassword', '');
            // this.$store.commit('setEmail', '');
            this.$router.push('/')
        },
        goTaskCurrent(task) {
            let taskId = task.id
            this.$router.push({ path: "/Project", query: { id: taskId } })
        },
        takeTask(id) {
            axios.get(this.$store.state.baseUrl + '/bind_project/' + id + '/' + this.$store.state.username)
                .then((response) => {
                    this.alertV("Binding Successful",'success')
                    window.location.reload()
                })
                .catch((error) => {
                    this.alertV("Binding Failed",'error')
                });
        },
        BindByID() {
            if (this.TaskID) {
                this.takeTask(this.TaskID)
                this.TaskID = ''
            }
        },
        addATag() {
            if (this.addTag !== "") {
                this.Tag.push(this.addTag)
                this.addTag = ""
            }
        },
        addAQuestion() {
            if (this.addQuestion !== "") {
                this.Question.push(this.addQuestion)
                this.QustionOptionType.push("SingleChoice")
                this.QuestionOptions.push([]),
                    this.addQuestion = ""
            }
        },
        delQuestion(i) {
            this.QuestionOptions.splice(i, 1);
            this.Question.splice(i, 1);
            this.QuestionAddOption.splice(i, 1);
        },
        addAQuestionOption(i) {
            if (this.QuestionAddOption[i] !== "") {
                this.QuestionOptions[i].push(this.QuestionAddOption[i])
                this.QuestionAddOption[i] = ""
            }
        },

        delOption(index, i) {
            if (this.QuestionOptions && this.QuestionOptions[index]) {
                this.QuestionOptions[index].splice(i, 1);
            }
        },
        delTag(i) {
            this.Tag.splice(i, 1)
        },
        createTaskPop() {
            this.dialog = true
            let currentDate = new Date();
            currentDate.setDate(currentDate.getDate() + 7);
            this.dueTime = currentDate.toISOString().substring(0, 16);
        },
        closePop() { //默认值在该函数内设置
            this.FeedbackType = this.config.feedback_type[0],
                this.Feedback_Select = 0,
                this.dataset_path = "",
                this.file = '',
                this.ProjectName = "project #n",
                this.dueTime = "",
                this.DatasetType = 'Existed',
                this.Domain = -1,
                this.Task = -1,
                this.Environment = -1,
                this.QueryNum = this.config.query_num.default,
                this.fps = this.config.fps.default,
                this.QueryLength = this.config.query_length.default,
                this.Description = "",
                this.Instruction = `<p>Enter the project instruction for annotators.</p>`,
                this.addQuestion = '',
                this.Question = [],
                this.QustionOptionType = [],
                this.QuestionAddOption = [],
                this.QuestionOptions = [],
                this.visibility = true,
                this.Mode = this.config.mode[0],
                this.SamplerType = this.config.sampler_type[0],
                this.addTag = "",
                this.Tag = [],
                this.VideoWidth = this.config.video_width.default
            this.VideoHeight = this.config.video_height.default
            this.queryNumRules = [
                v => !!v || 'Cannot be empty',
                v => !isNaN(parseFloat(v)) && isFinite(v) || 'Must be a number',
                v => (v >= this.config.query_num.minimum && v <= this.config.query_num.maximum) || 'Must be between ' + this.config.query_num.minimum + ' and ' + this.config.query_num.maximum
            ],
                this.queryLengthRules = [
                    v => !!v || 'Cannot be empty',
                    v => !isNaN(parseFloat(v)) && isFinite(v) || 'Must be a number',
                    v => (v >= this.config.query_length.minimum && v <= this.config.query_length.maximum) || 'Must be between ' + this.config.query_length.minimum + ' and ' + this.config.query_length.maximum
                ],
                this.VideoWidthRules = [
                    v => !!v || 'Cannot be empty',
                    v => !isNaN(parseFloat(v)) && isFinite(v) || 'Must be a number',
                    v => (v >= this.config.video_width.minimum && v <= this.config.video_width.maximum) || 'Must be between ' + this.config.video_width.minimum + ' and ' + this.config.video_width.maximum
                ],
                this.VideoHeightRules = [
                    v => !!v || 'Cannot be empty',
                    v => !isNaN(parseFloat(v)) && isFinite(v) || 'Must be a number',
                    v => (v >= this.config.video_height.minimum && v <= this.config.video_height.maximum) || 'Must be between ' + this.config.video_height.minimum + ' and ' + this.config.video_height.maximum

                ],
                this.dialog = false
        },
        findLabel(value, datasets) {
            for (const dataset of datasets) {
                if (dataset.value === value) {
                    return dataset.label;
                }
                if (dataset.children && dataset.children.length > 0) {
                    const label = this.findLabel(value, dataset.children);
                    if (label) {
                        return label;
                    }
                }
            }
            return null;
        },
        createTask() {
            console.log(this.dueTime)
            console.log(this.isValidInvisibleQuestion)
            if (this.$refs.createForm.validate() && this.isValidInvisibleQuestion) {
                let Tag = `${this.Tag.join(',')}`
                let ques = {};
                this.Question.forEach((question, index) => {
                    ques[question.toString()] = this.QuestionOptions[index];
                });
                let datasets = this.config.exsited_datasets
                let domain_name = this.findLabel(this.Domain, datasets)
                let task_name = this.findLabel(this.Task, datasets)
                let env_name = this.findLabel(this.Environment, datasets)

                axios.post(this.$store.state.baseUrl + '/create_new_project/' + this.$store.state.username, {
                    project_name: this.ProjectName,
                    description: this.Description,
                    due_time: this.formatDateTime(this.dueTime),
                    visibility: Boolean(this.visibility),
                    dataset_path: this.dataset_path,
                    domain: domain_name,
                    task: task_name,
                    environment_name: env_name,
                    instruction: this.Instruction,
                    mode: this.Mode,
                    sampler_type: this.SamplerType,
                    feedback_type: this.FeedbackType,
                    query_num: this.QueryNum,
                    query_length: this.QueryLength,
                    video_width: this.VideoWidth,
                    video_height: this.VideoHeight,
                    fps: this.fps,
                    question: ques,
                    tag: Tag,
                })
                    .then((response) => {
                        console.log(response.data)
                        this.alertV("Creation Successful",'success')
                        this.closePop()
                        window.location.reload()
                    })
                    .catch((err) => {
                        console.log(err)
                        this.alertV("Creation Failed",'error')
                    })
            } else {
                this.alertV(`We've noticed that some of the information you submitted may not meet our requirements. Please carefully check the following:

Ensure that all required fields have been filled out.
Check if the data format you entered is correct.
Questions and options cannot be left empty.`,'error')
            }
        },
        formatDateTime(dateTimeStr) {
            const date = new Date(dateTimeStr);
            const year = date.getFullYear();
            const month = date.getMonth() + 1;
            const day = date.getDate();
            const hours = date.getHours();
            const minutes = date.getMinutes();
            const seconds = date.getSeconds();
            const formattedDate = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
            const formattedTime = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
            return `${formattedDate} ${formattedTime}`;
        },
        validateFile(file) {
            if (!file) return;
            const validExtensions = ['h5', 'hdf5'];
            const extension = file.name.split('.').pop().toLowerCase();
            this.file = file
            // this.uploadFile()
            if (!validExtensions.includes(extension)) {
                this.$refs.fileInput.reset(); // 清空选择的文件
                this.alertV('Only .h5 or .hdf5 files are accepted.',"error");
            }
        },
        handleChange(value, selectedData) {
            console.log(selectedData)
            this.selected_dataset = selectedData[selectedData.length - 1].__label
            this.Domain = selectedData[0].value
            this.Task = selectedData[1].value
            this.Environment = selectedData[2].value
        },
        openView(id) {
            this.viewDialog = true
            axios.get(this.$store.state.baseUrl + '/project/' + id + "/" + this.$store.state.username)
                .then((response) => {
                    console.log(response.data.project)
                    let r = response.data.project
                    let data = {
                        project_id: r.project_id, project_name: r.project_name, description: r.description, due_time: this.formatDateTime(r.due_time),
                        visibility: r.visibility, dataset_path: r.dataset_path, domain: r.domain, task: r.task, environment_name: r.environment_name,
                        instruction: r.instruction, mode: r.mode, sampler_type: r.sampler_type, feedback_type: r.feedback_type, query_num: r.query_num,
                        query_length: r.query_length, video_width: r.video_width, video_height: r.video_height, fps: r.fps, creator: r.creator, create_time: this.formatDateTime(r.create_time),
                        status: r.status, annotation_num: r.annotation_num, question: r.question
                    }
                    this.view = data
                })
                .catch(() => {

                })
        },
        closeView() {
            this.viewDialog = false
        },
        selectFeedback(i, item) {
            this.Feedback_Select = i
            this.FeedbackType = item.type
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
}

.topBar {
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
    margin-right: 10px;
}

.avatar {
    height: 30px;
    width: 30px;
    margin-left: 24px;
}

.currentTask {
    width: 100vw;
    height: calc(60vh - 48px);
    display: flex;
    flex-direction: column;
}

.title {
    width: 100vw;
    height: 50px;
    padding-top: 10px;
    padding-left: 20px;
}

.currentTaskMain {
    height: calc(60vh - 98px);
    width: 100vw;
    overflow-y: auto;
}

.taskCard {
    background-color: #fff;
    border-radius: 6px;
    height: 150px;
    width: 23%;
    margin: 0 1%;
    margin-bottom: 30px;
    box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
}

.cardTitle {
    height: 45px;
    width: 100%;
    font-size: 20px;
    padding-left: 20px;
    padding-right: 20px;
    padding-top: 10px;
    display: flex;
    justify-content: space-between;
}

.cardEnv {
    height: 30px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-left: 20px;
    padding-right: 20px;
    color: rgba(0, 0, 0, 0.7);
}

.cardNumber {
    height: 45px;
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-left: 20px;
    padding-right: 20px;
    border-bottom: 1px solid rgba(0, 0, 0, 0.3);
    color: rgba(0, 0, 0, 0.7);
}

.cardNumber img {
    height: 16px;
    width: 16px;
    margin-right: 5px;
}

.cardBottom {
    height: 50px;
    padding-left: 20px;
    padding-right: 20px;
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.cardBottom img {
    height: 24px;
    width: 24px;
}

.content-empty {
    height: calc(100% - 50px);
    width: 100vw;
    margin-bottom: 50px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.content {
    top: 48px;
    left: 0;
    width: 100%;
    display: flex;
    padding: 10px 20px;
    flex-wrap: wrap;
}

.taskPool {
    box-shadow: 0px 0px 20px 0px rgba(0, 0, 0, 0.1);
    width: 100vw;
    height: 40vh;
}

.taskPoolMain {
    height: calc(40vh - 50px);
    width: 100vw;
    overflow-y: auto;
}

/* 创建任务dialog */
.projectName {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 50px;
}

.createInput {
    width: 80%;
}

.createInputTime {
    /* 添加你需要的样式，使其外观与原生的日期时间选择器相似 */
    width: 80%;
    height: 40px;
    border: 1px solid #909090;
    padding: 0.6rem 1rem;
    border-radius: 4px;
    font-size: 1rem;
    line-height: 1.5;
    color: #495057;
    background-color: #fff;
    background-clip: padding-box;
    transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
    outline-color: #007bff !important;
}

.LabelSetup {
    width: 100%;
    height: auto;
    display: flex;
    flex-wrap: wrap;
    padding: 30px 55px;

}

.feedbackItem {
    display: flex;
    flex-direction: column;
    align-items: center;
    border-radius: 10px;
    /* border: 1px solid #333333; */
    box-shadow: 0px 1px 10px 0px rgba(0, 0, 0, 0.2);
    margin: 10px;
}

.feedbackItem_activate {
    display: flex;
    flex-direction: column;
    align-items: center;
    border-radius: 10px;
    border: 3px solid #333333;
    box-shadow: 0px 1px 10px 0px rgba(0, 0, 0, 0.2);
    margin: 7px;
}

.feedbackImg {
    height: 130px;
    width: 200px;
    border-radius: 10px 10px 0 0;
}

.feedbackTitle {
    height: 30px;
    font-size: 24px;
    width: 200px;
    background-color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 0 0 10px 10px;
}

.feedbackTitle p {
    height: 30px;
    line-height: 30px;
    font-size: 24px;
    margin-bottom: 0;
}

.view_item {
    font-size: 18px;
    width: 80%;
}

.creatingMask {
    position: absolute;
    border-radius: 6px;
    height: 100%;
    width: 100%;
    background-color: rgba(72, 72, 72, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

</style>