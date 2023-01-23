const scheduleItemInitialState = () => ({
    cron: '0 0 0 0 0',
    cron_radio: 'custom',
    active: true,
    name: '',
    id: null,
    test_params: [],
    errors: {}
})

const ScheduleItem = {
    props: [...Object.keys(scheduleItemInitialState()), 'schedule_id'],
    emits: [
        ...Object.keys(scheduleItemInitialState()).filter(item => !['id', 'errors'].includes(item)).map(item => `update:${item}`),
        'delete'
    ],
    delimiters: ['[[', ']]'],
    data() {
        return {
            periods: ['daily', 'weekly', 'monthly', 'yearly', 'custom'],
            test_params_open: false,
        }
    },
    mounted() {
        this.test_params_table.ready(() => {
            this.test_params_table.bootstrapTable()
            this.test_params_table.bootstrapTable('load', this.test_params)
            this.test_params_table.on('all.bs.table', (e) => {
                this.$emit('update:test_params', this.test_params_table.bootstrapTable('getData'))
                this.test_params_table.find('.selectpicker').selectpicker('render')
            })
            this.test_params_table.find('.selectpicker').selectpicker('render')
        })
    },
    methods: {
        handleInputChange(e) {
            this.$emit('update:cron_radio', e.target.value)
            const today = new Date()
            switch (e.target.value) {
                case 'daily':
                    this.$emit('update:cron',
                        `${today.getMinutes()} ${today.getHours()} * * *`)
                    break
                case 'weekly':
                    this.$emit('update:cron',
                        `${today.getMinutes()} ${today.getHours()} * * ${today.getDay()}`)
                    break
                case 'monthly':
                    this.$emit('update:cron',
                        `${today.getMinutes()} ${today.getHours()} ${today.getDate()} * *`)
                    break
                case 'yearly':
                    this.$emit('update:cron',
                        `${today.getMinutes()} ${today.getHours()} ${today.getDate()} ${today.getMonth() + 1} *`)
                    break
                default:
            }
        },
    },
    watch: {
        errors(newE, oldE) {
            if (!!newE?.test_params) {
                const [row, col_name, ..._] = newE.test_params.loc
                // const get_col_by_name = name => $(`#security_test_params thead th[data-field=${name}]`).index()
                const get_col_by_name = name => $(`#${this.test_params_id} thead th[data-field=${name}]`).index()
                $(`#${this.test_params_id} tr[data-index=${row}] td:nth-child(${get_col_by_name(col_name) + 1}) input`)
                    .addClass('is-invalid')
                    .next('div.invalid-tooltip-custom')
                    .text(newE.test_params.msg)
            } else {
                $(`#${this.test_params_id}`).removeClass('is-invalid')
            }


        }
    },
    computed: {
        test_params_id() {
            return `schedule_test_params_${this.schedule_id}`
        },
        test_params_table() {
            return $(`#${this.test_params_id} table.params-table`)
        },

    },
    template: `
        <div class="col-12" >
            <div class="card card-row-1">
                <div class="card-header">
                    <div class="d-flex">
                        <h7 class="flex-grow-1">Set schedule</h7>
                        <button type="button" class="btn btn-24 btn-action"
                            @click="$emit('delete', schedule_id)"
                        >
                            <i class="fas fa-trash"></i>
                        </button>
                        <label class="custom-toggle">
                            <input type="checkbox"
                                @change="$emit('update:active', $event.target.checked)"
                                :checked="active"
                            >
<!--                            <span class="custom-toggle-slider rounded-circle"></span>-->
                            <span class="custom-toggle_slider round"></span>
                        </label>
                    </div>
                </div>
                <div class="card-body">
                    <div class="row justify-content-around">
                        <div class="col-6 row row-cols-1">
                            <label>
                                <h9>Schedule name</h9>
                                <input class="form-control form-control-alternative" type="text"
                                   placeholder="Name"
                                   :value="name"
                                   @change="$emit('update:name', $event.target.value)"
                                   :class="{ 'is-invalid': errors?.name }"
                                >
                                <div class="invalid-feedback">[[ errors?.name?.msg ]]</div>
                            </label>
                        </div>
                        <div class="col-6 row row-cols-1">
                            <div class="col-12">
                                <h9>Schedule</h9>
                            </div>
                            <div class="col-12">
                                <div class="col-12 form-group d-flex justify-content-center mt-3">
                                    <div class="form-check form-check-inline" 
                                        v-for="t in periods"
                                    >
                                        <label>
                                            <input type="radio" class="form-check-input align-middle" 
                                                :value="t"
                                                :name="'cron_radio_' + schedule_id"
                                                :checked="cron_radio === t"
                                                @change="handleInputChange"
                                            >
                                            <h13 class="form-check-label text-capitalize">[[ t ]]</h13>
                                        </label>
                                    </div>
                                </div>
                                <div class="col-12 input-group d-flex justify-content-around p-4 m-auto"
                                    style="
                                        border: 1px solid #DBE2E8;
                                        box-sizing: border-box;
                                        border-radius: 4px;
                                    "
                                >
                                    <input class="form-control form-control-alternative text-center" type="text"
                                       placeholder="* * * * *"
                                       :value="cron"
                                       :disabled="cron_radio !== 'custom'"
                                       @change="$emit('update:cron', $event.target.value)"
                                       :class="{ 'is-invalid': errors?.cron }"
                                    >
                                    <div class="invalid-feedback">[[ errors?.cron?.msg ]]</div>
                                </div>
                                <div class="col-12">
                                    <h13 style="color: var(--basic)">
                                        <i class="fa fa-info-circle"></i> Symbols
                                    </h13>
                                </div>

                            </div>
                        </div>
                    </div>
                    <div class="row mb-3">
                        <div class="mb-1"
                             aria-expanded="false"
                             data-toggle="collapse"
                             style="cursor: pointer"
                             :data-target="'#' + test_params_id"
                             @click="test_params_open = !test_params_open"
                        >
                            <h7 style="color: var(--basic)">
                                Test parameters <i class="fa" 
                                    :class="test_params_open ? 'fa-angle-down' : 'fa-angle-right'"></i>
                            </h7>
                            <p>
                                <h13>Specify parameters for test runs</h13>
                            </p>
                        </div>
                        <div class="collapse col-12 pl-0" :id="test_params_id">
                            <slot></slot>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `
}

const SchedulingApp = {
    delimiters: ['[[', ']]'],
    props: ['instance_name', 'params_table'],
    components: {
        'schedule-item': ScheduleItem
    },
    data() {
        return {
            schedules_items: [],
            errors: {}
        }
    },
    mounted() {
        window.SchedulingSection = {
            Manager: () => ({
                get: () => this.schedules_items,
                set: values => {
                    this.schedules_items = values.map(item => ({...scheduleItemInitialState(), ...item}))
                },
                clear: () => this.schedules_items = [],
                setError: data => {
                    const [_, index, field, ...rest] = data.loc

                    if (this.errors[index]) {
                        this.errors[index][field] = {loc: rest, msg: data.msg}
                    } else {
                        this.errors[index] = {[field]: {loc: rest, msg: data.msg}}
                    }
                },
                clearErrors: () => this.errors = {}
            })
        }
    },
    methods: {
        handleDeleteItem(schedule_id) {
            this.schedules_items.splice(schedule_id, 1)
        },
        handleAddItem() {
            this.schedules_items.push(scheduleItemInitialState())
        }
    },
    template: `
        <div class="modal-body">
            <div class="row">
                <div class="col mb-3">
                    <p class="font-h5 font-bold font-uppercase">Scheduling</p>
                    <p class="font-h6 font-weight-400">You can create several schedules of this test with different parameters</p>
                </div>
        
                <schedule-item
                        v-for="(item, index) in schedules_items"
                        :key="index"
                        v-model:name="item.name"
                        v-model:active="item.active"
                        v-model:cron="item.cron"
                        v-model:cron_radio="item.cron_radio"
                        v-model:test_params="item.test_params"
                        :schedule_id="index"
                        @delete="handleDeleteItem"
                        :errors="errors[index]"
                >
                    <div v-html="params_table"></div>
                </schedule-item>
            </div>
            <button type="button" class="btn btn-sm btn-secondary"
                    @click.prevent="handleAddItem"
            >
                <span class="fa fa-plus mr-2"></span> Add schedule
            </button>
        </div>
    `
}


register_component('scheduling', SchedulingApp)
