import { IChart } from "@mrblenny/react-flow-chart";

export declare type FairCell = {
    title               : string;
    task_name           : string;
    original_source     : string;
    inputs              : [];
    outputs             : [];
    params              : [];
    confs               : {};
    dependencies        : [];
    chart_obj           : IChart;
    node_id             : string;
    container_source    : string;
    global_conf         : {};
}

export declare type Repository = {

    name    : string;
    url     : string;
    token   : string;
}

export declare type Registry = {

    name    : string;
    url     : string;
}