create table projects
(
    name varchar not null,
    group_id varchar not null,
    artifact_id varchar not null,
    version varchar not null,
    has_sources boolean not null,

    jars_download_status int not null,
    jars_unpacking_status int not null,
    language_detection_status int not null,
    language_persistence_status int not null,
    metrics_calculation_status int not null,
    metrics_persistence_status int not null,
    pattern_detection_status int not null,
    pattern_persistence_status int not null,
    java_version_detection_status int not null,
    java_version_persistence_status int not null,
    java_version int,

    constraint projects_pkey
        primary key (name)
);

create table project_languages
(
    project varchar not null,
    name varchar not null,
    fraction float not null,
    constraint project_languages_pkey
        primary key (project, name),
    constraint project_languages_project_fkey
        foreign key (project) references projects on delete cascade
);

create table project_metrics
(
    project varchar not null,
    tl int not null,
    bl int not null,
    ci int not null,
    co int not null,
    constraint project_metrics_pkey
        primary key (project),
    constraint project_metrics_project_fkey
        foreign key (project) references projects on delete cascade
);

create table pakkages
(
    project varchar not null,
    name varchar not null,
    constraint pakkages_pkey
        primary key (name),
    constraint pakkages_project_fkey
        foreign key (project) references projects on delete cascade
);

create table pakkage_metrics
(
    pakkage varchar not null,
    abstractness float not null,
    avcc float not null,
    cumulative_number_of_comment_lines int not null,
    cumulative_number_of_comments int not null,
    distance float not null,
    fanin int not null,
    fanout int not null,
    halstead_cumulative_bugs float not null,
    halstead_cumulative_length int not null,
    halstead_cumulative_volume float not null,
    halstead_effort float not null,
    instability float not null,
    loc int not null,
    maintainability_index float not null,
    maintainability_index_nc float not null,
    maxcc int not null,
    number_of_classes int not null,
    number_of_methods int not null,
    number_of_statements int not null,
    rvf int not null,
    tcc int not null,
    constraint pakkage_metrics_pkey
        primary key (pakkage),
    constraint pakkage_metrics_pakkage_fkey
        foreign key (pakkage) references pakkages on delete cascade
);

create table clazzes
(
    pakkage varchar not null,
    name varchar not null,
    constraint clazzes_pkey
        primary key (name),
    constraint clazzes_pakkage_fkey
        foreign key (pakkage) references pakkages on delete cascade
);

create table clazz_metrics
(
    clazz varchar not null,
    avcc float not null,
    cbo int not null,
    coh float not null,
    cumulative_number_of_comment_lines int not null,
    cumulative_number_of_comments int not null,
    dit int not null,
    fan_in int not null,
    fan_out int not null,
    halstead_cumulative_bugs float not null,
    halstead_cumulative_length int not null,
    halstead_cumulative_volume float not null,
    halstead_effort float not null,
    lcom float not null,
    lcom2 float not null,
    loc int not null,
    maintainability_index float not null,
    maintainability_index_nc float not null,
    maxcc int not null,
    message_passing_coupling int not null,
    number_of_commands int not null,
    number_of_methods int not null,
    number_of_queries int not null,
    number_of_statements int not null,
    number_of_sub_classes int not null,
    number_of_super_classes int not null,
    response_for_class int not null,
    reuse_ration float not null,
    revf float not null,
    six float not null,
    specialization_ration float not null,
    tcc int not null,
    unweighted_class_size int not null,
    constraint clazz_metrics_pkey
        primary key (clazz),
    constraint clazz_metrics_clazz_fkey
        foreign key (clazz) references clazzes on delete cascade
);

create table methods
(
    clazz varchar not null,
    name varchar not null,
    constraint methods_pkey
        primary key (name),
    constraint methods_clazz_fkey
        foreign key (clazz) references clazzes on delete cascade
);

create table method_metrics
(
    method varchar not null,
    cyclomatic_complexity int not null,
    halstead_bugs float not null,
    halstead_difficulty float not null,
    halstead_effort float not null,
    halstead_length int not null,
    halstead_vocabulary int not null,
    halstead_volume float not null,
    loc int not null,
    max_depth_of_nesting int not null,
    number_of_arguments int not null,
    number_of_casts int not null,
    number_of_comment_lines int not null,
    number_of_comments int not null,
    number_of_expressions int not null,
    number_of_loops int not null,
    number_of_operands int not null,
    number_of_operators int not null,
    number_of_statements int not null,
    number_of_variable_declarations int not null,
    number_of_variable_references int not null,
    total_nesting int not null,
    constraint method_metrics_pkey
        primary key (method),
    constraint method_metrics_method_fkey
        foreign key (method) references methods on delete cascade
);

create table pattern_instances
(
    id uuid not null,
    project varchar not null,
    pattern varchar not null,
    constraint pattern_instances_pkey
        primary key (id),
    constraint pattern_instances_pattern
        foreign key (project) references projects on delete cascade
);

create table pattern_roles
(
    id uuid not null,
    instance_id uuid not null,
    role varchar not null,
    element varchar not null,
    constraint pattern_roles_pkey
        primary key (id),
    constraint pattern_roles_instance_id
        foreign key (instance_id) references pattern_instances on delete cascade
);
