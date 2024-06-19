import { IChart } from "@mrblenny/react-flow-chart";

export declare type VRECell = {
    title               : string;
    task_name           : string;
    original_source     : string;
    base_image          : {};
    inputs              : [];
    outputs             : [];
    params              : [];
    param_values        : { [name: string]: string | null };
    confs               : {};
    dependencies        : [];
    types               : { [id: string] : string | null },
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