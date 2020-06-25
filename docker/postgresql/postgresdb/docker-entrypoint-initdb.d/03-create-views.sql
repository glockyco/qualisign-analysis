create extension if not exists tablefunc;

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

---- DENORMALIZATION ----

drop materialized view if exists mv_projects cascade;

-- fully processed projects
create materialized view mv_projects as
    select
        projects.name as project_name_full,
        projects.version,
        projects.java_version
    from projects
    inner join project_languages on projects.name = project_languages.project
    where projects.pattern_persistence_status = 1
    and project_languages.name = 'Java'
    and project_languages.fraction = 1
    order by project_name_full;

create unique index on mv_projects (project_name_full);

-- packages in fully processed projects
create materialized view mv_pakkages as
    select
        mv_projects.project_name_full,
        pakkages.name as pakkage_name_full--,
        --replace(pakkages.name, mv_projects.project_name_full || '.', '') as pakkage_name_short
    from mv_projects
    inner join pakkages on mv_projects.project_name_full = pakkages.project;

create unique index on mv_pakkages (pakkage_name_full);

-- classes in fully processed projects
create materialized view mv_clazzes as
    select
        mv_pakkages.project_name_full,
        mv_pakkages.pakkage_name_full,
        clazzes.name as clazz_name_full--,
        --replace(clazzes.name, mv_pakkages.project_name_full || '.', '') as clazz_name_short
    from clazzes
    inner join mv_pakkages on mv_pakkages.pakkage_name_full = clazzes.pakkage;

create unique index on mv_clazzes (clazz_name_full);

create materialized view mv_clazz_metrics_ckjm as
    select
        clazzes.project_name_full,
        clazzes.pakkage_name_full,
        clazzes.clazz_name_full,
        metrics.amc,
        metrics.ca,
        metrics.cbm,
        metrics.cc,
        metrics.ce,
        metrics.ic,
        metrics.lcom,
        metrics.lcom3,
        metrics.loc,
        metrics.noc,
        metrics.rfc,
        metrics.wmc,
        metrics.dit as ana,
        metrics.dam as dam,
        metrics.cbo as dcc,
        metrics.cam as cam,
        metrics.moa as moa,
        metrics.mfa as mfa,
        metrics.nop as nop,
        metrics.npm as cis,
        metrics.nom as nom
    from clazz_metrics_ckjm as metrics
    inner join mv_clazzes as clazzes on clazzes.clazz_name_full = metrics.clazz;

create unique index on mv_clazz_metrics_ckjm (clazz_name_full);

create materialized view mv_project_metrics_ckjm as
    select * from crosstab(
        $$
            select project_name_full, 'dsc' as metric, count(*) as value from mv_clazz_metrics_ckjm group by project_name_full
            union all
            select project_name_full, 'noh' as metric, count(*) as value from mv_clazz_metrics_ckjm where noc = 0 group by project_name_full
            order by project_name_full, metric
        $$,
        $$
            values ('dsc'), ('noh')
        $$
    ) as ct(project_name_full text, dsc int, noh int);

create unique index on mv_project_metrics_ckjm (project_name_full);

--------------------------------------------------------------------------------

create materialized view mv_clazzes_metrics as
    select
        *,
        - 0.25 * dcc + 0.25 * cam + 0.50 * cis + 0.50 * dsc as reusability,
        + 0.25 * dam - 0.25 * dcc + 0.50 * moa + 0.50 * nop as flexibility,
        - 0.33 * ana + 0.33 * dam - 0.33 * dcc + 0.33 * cam - 0.33 * nop -0.33 * nom - 0.33 * dsc as understandability,
        + 0.12 * cam + 0.22 * nop + 0.22 * cis + 0.22 * dsc + 0.22 * noh as functionality,
        + 0.50 * ana - 0.50 * dcc + 0.50 * mfa + 0.50 * nop as extendibility,
        + 0.20 * ana + 0.20 * dam + 0.20 * moa + 0.20 * mfa + 0.20 * nop as effectiveness
    from (
        select
            clazz_metrics.project_name_full,
            clazz_metrics.pakkage_name_full,
            clazz_metrics.clazz_name_full,
            ---
            clazz_metrics.amc,
            clazz_metrics.ca,
            clazz_metrics.cbm,
            clazz_metrics.cc,
            clazz_metrics.ce,
            clazz_metrics.ic,
            clazz_metrics.lcom,
            clazz_metrics.lcom3,
            clazz_metrics.loc,
            clazz_metrics.noc,
            clazz_metrics.rfc,
            clazz_metrics.wmc,
            ---
            project_metrics.dsc,
            project_metrics.noh,
            clazz_metrics.ana,
            clazz_metrics.dam,
            clazz_metrics.dcc,
            clazz_metrics.cam,
            clazz_metrics.moa,
            clazz_metrics.mfa,
            clazz_metrics.nop,
            clazz_metrics.cis,
            clazz_metrics.nom
            ---
        from mv_clazz_metrics_ckjm as clazz_metrics
        inner join mv_project_metrics_ckjm as project_metrics on clazz_metrics.project_name_full = project_metrics.project_name_full
    ) as clazz_metrics_temp;

create unique index on mv_clazzes_metrics (clazz_name_full);

create materialized view mv_pakkages_metrics as
    select
        clazz_metrics.project_name_full,
        clazz_metrics.pakkage_name_full,
        count(clazz_metrics.clazz_name_full) as clazz_count,
        ---
        avg(clazz_metrics.amc) as amc_avg,
        avg(clazz_metrics.ca) as ca_avg,
        avg(clazz_metrics.cbm) as cbm_avg,
        avg(clazz_metrics.cc) as cc_avg,
        avg(clazz_metrics.ce) as ce_avg,
        avg(clazz_metrics.ic) as ic_avg,
        avg(clazz_metrics.lcom) as lcom_avg,
        avg(clazz_metrics.lcom3) as lcom3_avg,
        avg(clazz_metrics.loc) as loc_avg,
        sum(clazz_metrics.loc) as loc_sum,
        avg(clazz_metrics.noc) as noc_avg,
        avg(clazz_metrics.rfc) as rfc_avg,
        avg(clazz_metrics.wmc) as wmc_avg,
        ---
        avg(clazz_metrics.dsc) as dsc_avg,
        avg(clazz_metrics.noh) as noh_avg,
        avg(clazz_metrics.ana) as ana_avg,
        avg(clazz_metrics.dam) as dam_avg,
        avg(clazz_metrics.dcc) as dcc_avg,
        avg(clazz_metrics.cam) as cam_avg,
        avg(clazz_metrics.moa) as moa_avg,
        avg(clazz_metrics.mfa) as mfa_avg,
        avg(clazz_metrics.nop) as nop_avg,
        avg(clazz_metrics.cis) as cis_avg,
        avg(clazz_metrics.nom) as nom_avg,
        ---
        avg(clazz_metrics.reusability) as reusability_avg,
        avg(clazz_metrics.flexibility) as flexibility_avg,
        avg(clazz_metrics.understandability) as understandability_avg,
        avg(clazz_metrics.functionality) as functionality_avg,
        avg(clazz_metrics.extendibility) as extendibility_avg,
        avg(clazz_metrics.effectiveness) as effectiveness_avg
    from mv_clazzes_metrics as clazz_metrics
    group by project_name_full, pakkage_name_full;

create unique index on mv_pakkages_metrics (pakkage_name_full);

create materialized view mv_projects_metrics as
    select
        clazz_metrics.project_name_full,
        count(clazz_metrics.clazz_name_full) as clazz_count,
        ---
        avg(clazz_metrics.amc) as amc_avg,
        avg(clazz_metrics.ca) as ca_avg,
        avg(clazz_metrics.cbm) as cbm_avg,
        avg(clazz_metrics.cc) as cc_avg,
        avg(clazz_metrics.ce) as ce_avg,
        avg(clazz_metrics.ic) as ic_avg,
        avg(clazz_metrics.lcom) as lcom_avg,
        avg(clazz_metrics.lcom3) as lcom3_avg,
        avg(clazz_metrics.loc) as loc_avg,
        sum(clazz_metrics.loc) as loc_sum,
        avg(clazz_metrics.noc) as noc_avg,
        avg(clazz_metrics.rfc) as rfc_avg,
        avg(clazz_metrics.wmc) as wmc_avg,
        ---
        avg(clazz_metrics.dsc) as dsc_avg,
        avg(clazz_metrics.noh) as noh_avg,
        avg(clazz_metrics.ana) as ana_avg,
        avg(clazz_metrics.dam) as dam_avg,
        avg(clazz_metrics.dcc) as dcc_avg,
        avg(clazz_metrics.cam) as cam_avg,
        avg(clazz_metrics.moa) as moa_avg,
        avg(clazz_metrics.mfa) as mfa_avg,
        avg(clazz_metrics.nop) as nop_avg,
        avg(clazz_metrics.cis) as cis_avg,
        avg(clazz_metrics.nom) as nom_avg,
        ---
        avg(clazz_metrics.reusability) as reusability_avg,
        avg(clazz_metrics.flexibility) as flexibility_avg,
        avg(clazz_metrics.understandability) as understandability_avg,
        avg(clazz_metrics.functionality) as functionality_avg,
        avg(clazz_metrics.extendibility) as extendibility_avg,
        avg(clazz_metrics.effectiveness) as effectiveness_avg
    from mv_clazzes_metrics as clazz_metrics group by project_name_full;

create unique index on mv_projects_metrics (project_name_full);

--------------------------------------------------------------------------------

-- patterns in fully processed projects
create materialized view mv_pattern_instances as
    select
        pattern_instances.project as project_name_full,
        pattern_instances.id as pattern_id,
        pattern_instances.pattern
    from pattern_instances
    inner join mv_projects on pattern_instances.project = mv_projects.project_name_full;

create unique index on mv_pattern_instances (pattern_id);

-- pattern roles in fully processed projects
create materialized view mv_pattern_roles as
    select
        project_name_full,
        project_name_full || '.' || substring(clazz_name_short from '#"%#".%' for '#') as pakkage_name_full,
        project_name_full || '.' || clazz_name_short as clazz_name_full,
        pattern_id,
        role_id,
        pattern,
        role,
        element
    from (
        select
            mv_pattern_instances.project_name_full,
            mv_pattern_instances.pattern_id,
            pattern_roles.id as role_id,
            mv_pattern_instances.pattern,
            pattern_roles.role,
            pattern_roles.element,
            coalesce(substring(element from '#"%#"::%' for '#'), element) as clazz_name_short
        from pattern_roles
        inner join mv_pattern_instances on pattern_roles.instance_id = mv_pattern_instances.pattern_id
    ) as roles;
    --order by project_name_full, pattern_id, role;

create unique index on mv_pattern_roles (role_id);

--------------------------------------------------------------------------------

-- projects and the pattern roles that occur inside of them
create materialized view mv_projects_pattern_roles as
select mv_pattern_roles.*
from mv_pattern_roles
inner join mv_projects on mv_pattern_roles.project_name_full = mv_projects.project_name_full;

create unique index on mv_projects_pattern_roles (project_name_full, role_id);

-- packages and the pattern roles that occur inside of them
create materialized view mv_pakkages_pattern_roles as
select mv_pattern_roles.*
from mv_pattern_roles
inner join mv_pakkages on mv_pattern_roles.pakkage_name_full = mv_pakkages.pakkage_name_full;

create unique index on mv_pakkages_pattern_roles (pakkage_name_full, role_id);

-- classes and the patterns roles they are participating in
create materialized view mv_clazzes_pattern_roles as
select mv_pattern_roles.*
from mv_pattern_roles
inner join mv_clazzes on mv_pattern_roles.clazz_name_full = mv_clazzes.clazz_name_full;

create unique index on mv_clazzes_pattern_roles (clazz_name_full, role_id);

--------------------------------------------------------------------------------

-- projects and the patterns that occur inside of them
create materialized view mv_projects_patterns as
select distinct
    project_name_full,
    pattern_id,
    pattern
from mv_projects_pattern_roles;

create unique index on mv_projects_patterns (project_name_full, pattern_id);

-- packages and the patterns that occur inside of them
create materialized view mv_pakkages_patterns as
select distinct
    project_name_full,
    pakkage_name_full,
    pattern_id,
    pattern
from mv_pakkages_pattern_roles;

create unique index on mv_pakkages_patterns (pakkage_name_full, pattern_id);

-- classes and the patterns they are participating in
create materialized view mv_clazzes_patterns as
select distinct
    project_name_full,
    pakkage_name_full,
    clazz_name_full,
    pattern_id,
    pattern
from mv_clazzes_pattern_roles;

create unique index on mv_clazzes_patterns (clazz_name_full, pattern_id);

--------------------------------------------------------------------------------

create or replace function crosstab_project_patterns(text, text)
returns table (
    project_name_full text,
    adapter_count int,
    bridge_count int,
    chain_of_responsibility_count int,
    command_count int,
    composite_count int,
    decorator_count int,
    factory_method_count int,
    observer_count int,
    prototype_count int,
    proxy_count int,
    proxy2_count int,
    singleton_count int,
    state_count int,
    strategy_count int,
    template_method_count int,
    visitor_count int
) as '$libdir/tablefunc', 'crosstab_hash' language c stable strict;

create or replace function crosstab_pakkage_patterns(text, text)
returns table (
    pakkage_name_full text,
    adapter_count int,
    bridge_count int,
    chain_of_responsibility_count int,
    command_count int,
    composite_count int,
    decorator_count int,
    factory_method_count int,
    observer_count int,
    prototype_count int,
    proxy_count int,
    proxy2_count int,
    singleton_count int,
    state_count int,
    strategy_count int,
    template_method_count int,
    visitor_count int
) as '$libdir/tablefunc', 'crosstab_hash' language c stable strict;

create or replace function crosstab_clazz_patterns(text, text)
returns table (
    clazz_name_full text,
    adapter_count int,
    bridge_count int,
    chain_of_responsibility_count int,
    command_count int,
    composite_count int,
    decorator_count int,
    factory_method_count int,
    observer_count int,
    prototype_count int,
    proxy_count int,
    proxy2_count int,
    singleton_count int,
    state_count int,
    strategy_count int,
    template_method_count int,
    visitor_count int
) as '$libdir/tablefunc', 'crosstab_hash' language c stable strict;

--------------------------------------------------------------------------------

create materialized view mv_projects_pattern_counts as
    with pattern_counts_total as (
        select project_name_full, count(*) as pattern_count
        from mv_projects_patterns
        group by project_name_full
    ), pattern_counts_per_pattern as (
        select * from crosstab_project_patterns(
            $$
                select
                    project_name_full,
                    pattern,
                    count(*) as count
                from mv_projects_patterns
                group by project_name_full, pattern
                order by project_name_full, pattern
            $$,
            $$
                select distinct pattern from mv_projects_patterns order by pattern
            $$
        ) as pattern_counts
    )
    select
        mv_projects.project_name_full,
        coalesce(pattern_count, 0) as pattern_count,
        coalesce(adapter_count, 0) as adapter_count,
        coalesce(bridge_count, 0) as bridge_count,
        coalesce(chain_of_responsibility_count, 0) as chain_of_responsibility_count,
        coalesce(command_count, 0) as command_count,
        coalesce(composite_count, 0) as composite_count,
        coalesce(decorator_count, 0) as decorator_count,
        coalesce(factory_method_count, 0) as factory_method_count,
        coalesce(observer_count, 0) as observer_count,
        coalesce(prototype_count, 0) as prototype_count,
        coalesce(proxy_count, 0) as proxy_count,
        coalesce(proxy2_count, 0) as proxy2_count,
        coalesce(singleton_count, 0) as singleton_count,
        coalesce(state_count, 0) as state_count,
        coalesce(strategy_count, 0) as strategy_count,
        coalesce(template_method_count, 0) as template_method_count,
        coalesce(visitor_count, 0) as visitor_count
    from mv_projects
    left join pattern_counts_total on mv_projects.project_name_full = pattern_counts_total.project_name_full
    left join pattern_counts_per_pattern on mv_projects.project_name_full = pattern_counts_per_pattern.project_name_full;

create unique index on mv_projects_pattern_counts (project_name_full);

create materialized view mv_pakkages_pattern_counts as
    with pattern_counts_total as (
        select pakkage_name_full, count(*) as pattern_count
        from mv_pakkages_patterns
        group by pakkage_name_full
    ), pattern_counts_per_pattern as (
        select * from crosstab_pakkage_patterns(
            $$
                select
                    pakkage_name_full,
                    pattern,
                    count(*) as count
                from mv_pakkages_patterns
                group by pakkage_name_full, pattern
                order by pakkage_name_full, pattern
            $$,
            $$
                select distinct pattern from mv_pakkages_patterns order by pattern
            $$
        ) as pattern_counts
    )
    select
        mv_pakkages.project_name_full,
        mv_pakkages.pakkage_name_full,
        coalesce(pattern_count, 0) as pattern_count,
        coalesce(adapter_count, 0) as adapter_count,
        coalesce(bridge_count, 0) as bridge_count,
        coalesce(chain_of_responsibility_count, 0) as chain_of_responsibility_count,
        coalesce(command_count, 0) as command_count,
        coalesce(composite_count, 0) as composite_count,
        coalesce(decorator_count, 0) as decorator_count,
        coalesce(factory_method_count, 0) as factory_method_count,
        coalesce(observer_count, 0) as observer_count,
        coalesce(prototype_count, 0) as prototype_count,
        coalesce(proxy_count, 0) as proxy_count,
        coalesce(proxy2_count, 0) as proxy2_count,
        coalesce(singleton_count, 0) as singleton_count,
        coalesce(state_count, 0) as state_count,
        coalesce(strategy_count, 0) as strategy_count,
        coalesce(template_method_count, 0) as template_method_count,
        coalesce(visitor_count, 0) as visitor_count
    from mv_pakkages
    left join pattern_counts_total on mv_pakkages.pakkage_name_full = pattern_counts_total.pakkage_name_full
    left join pattern_counts_per_pattern on mv_pakkages.pakkage_name_full = pattern_counts_per_pattern.pakkage_name_full;

create unique index on mv_pakkages_pattern_counts (pakkage_name_full);

create materialized view mv_clazzes_pattern_counts as
    with pattern_counts_total as (
        select clazz_name_full, count(*) as pattern_count
        from mv_clazzes_patterns
        group by clazz_name_full
    ), pattern_counts_per_pattern as (
        select * from crosstab_clazz_patterns(
            $$
                select
                    clazz_name_full,
                    pattern,
                    count(*) as count
                from mv_clazzes_patterns
                group by clazz_name_full, pattern
                order by clazz_name_full, pattern
            $$,
            $$
                select distinct pattern from mv_clazzes_patterns order by pattern
            $$
        ) as pattern_counts
    )
    select
        mv_clazzes.project_name_full,
        mv_clazzes.pakkage_name_full,
        mv_clazzes.clazz_name_full,
        coalesce(pattern_count, 0) as pattern_count,
        coalesce(adapter_count, 0) as adapter_count,
        coalesce(bridge_count, 0) as bridge_count,
        coalesce(chain_of_responsibility_count, 0) as chain_of_responsibility_count,
        coalesce(command_count, 0) as command_count,
        coalesce(composite_count, 0) as composite_count,
        coalesce(decorator_count, 0) as decorator_count,
        coalesce(factory_method_count, 0) as factory_method_count,
        coalesce(observer_count, 0) as observer_count,
        coalesce(prototype_count, 0) as prototype_count,
        coalesce(proxy_count, 0) as proxy_count,
        coalesce(proxy2_count, 0) as proxy2_count,
        coalesce(singleton_count, 0) as singleton_count,
        coalesce(state_count, 0) as state_count,
        coalesce(strategy_count, 0) as strategy_count,
        coalesce(template_method_count, 0) as template_method_count,
        coalesce(visitor_count, 0) as visitor_count
    from mv_clazzes
    left join pattern_counts_total on mv_clazzes.clazz_name_full = pattern_counts_total.clazz_name_full
    left join pattern_counts_per_pattern on mv_clazzes.clazz_name_full = pattern_counts_per_pattern.clazz_name_full;

create unique index on mv_clazzes_pattern_counts (clazz_name_full);

--------------------------------------------------------------------------------

create materialized view mv_pakkages_pattern_clazz_counts as
    with pattern_clazz_counts_total as (
        select * from crosstab(
            $$
                select pakkage_name_full, 'overall_count' as type, count(*) as value from mv_clazzes_pattern_counts group by pakkage_name_full
                union all
                select pakkage_name_full, 'non_pattern_count' as type, count(*) as value from mv_clazzes_pattern_counts where pattern_count = 0 group by pakkage_name_full
                union all
                select pakkage_name_full, 'pattern_count' as type, count(*) as value from mv_clazzes_pattern_counts where pattern_count > 0 group by pakkage_name_full
                order by pakkage_name_full, type
            $$,
            $$
                values ('overall_count'), ('non_pattern_count'), ('pattern_count')
            $$
        ) as ct(pakkage_name_full text, overall_count int, non_pattern_count int, pattern_count int)
    ), pattern_clazz_counts_per_pattern as (
        select * from crosstab_pakkage_patterns(
            $$
                select
                    pakkage_name_full,
                    pattern,
                    count(*) as count
                from (
                    select
                        pakkage_name_full,
                        clazz_name_full,
                        pattern
                    from mv_clazzes_patterns
                    group by pakkage_name_full, clazz_name_full, pattern
                ) as pakkage_clazz_patterns
                group by pakkage_name_full, pattern
                order by pakkage_name_full, pattern
            $$,
            $$
                select distinct pattern from mv_clazzes_patterns order by pattern
            $$
        )
    )
    select
        mv_pakkages.project_name_full,
        mv_pakkages.pakkage_name_full,
        coalesce(overall_count, 0) as overall_count,
        coalesce(non_pattern_count, 0) as non_pattern_count,
        coalesce(pattern_count, 0) as pattern_count,
        coalesce(adapter_count, 0) as adapter_count,
        coalesce(bridge_count, 0) as bridge_count,
        coalesce(chain_of_responsibility_count, 0) as chain_of_responsibility_count,
        coalesce(command_count, 0) as command_count,
        coalesce(composite_count, 0) as composite_count,
        coalesce(decorator_count, 0) as decorator_count,
        coalesce(factory_method_count, 0) as factory_method_count,
        coalesce(observer_count, 0) as observer_count,
        coalesce(prototype_count, 0) as prototype_count,
        coalesce(proxy_count, 0) as proxy_count,
        coalesce(proxy2_count, 0) as proxy2_count,
        coalesce(singleton_count, 0) as singleton_count,
        coalesce(state_count, 0) as state_count,
        coalesce(strategy_count, 0) as strategy_count,
        coalesce(template_method_count, 0) as template_method_count,
        coalesce(visitor_count, 0) as visitor_count
    from mv_pakkages
    inner join pattern_clazz_counts_total on mv_pakkages.pakkage_name_full = pattern_clazz_counts_total.pakkage_name_full
    left join pattern_clazz_counts_per_pattern on mv_pakkages.pakkage_name_full = pattern_clazz_counts_per_pattern.pakkage_name_full;

create unique index on mv_pakkages_pattern_clazz_counts (pakkage_name_full);

create materialized view mv_projects_pattern_clazz_counts as (
    select
        project_name_full,
        sum(overall_count) as overall_count,
        sum(non_pattern_count) as non_pattern_count,
        sum(pattern_count) as pattern_count,
        sum(adapter_count) as adapter_count,
        sum(bridge_count) as bridge_count,
        sum(chain_of_responsibility_count) as chain_of_responsibility_count,
        sum(command_count) as command_count,
        sum(composite_count) as composite_count,
        sum(decorator_count) as decorator_count,
        sum(factory_method_count) as factory_method_count,
        sum(observer_count) as observer_count,
        sum(prototype_count) as prototype_count,
        sum(proxy_count) as proxy_count,
        sum(proxy2_count) as proxy2_count,
        sum(singleton_count) as singleton_count,
        sum(state_count) as state_count,
        sum(strategy_count) as strategy_count,
        sum(template_method_count) as template_method_count,
        sum(visitor_count) as visitor_count
    from mv_pakkages_pattern_clazz_counts
    group by project_name_full
);

create unique index on mv_projects_pattern_clazz_counts (project_name_full);

--------------------------------------------------------------------------------

create materialized view mv_pakkages_pattern_clazz_fractions as (
    select
        project_name_full,
        pakkage_name_full,
        overall_count,
        non_pattern_count::decimal / overall_count as non_pattern_fraction,
        pattern_count::decimal / overall_count as pattern_fraction,
        adapter_count::decimal / overall_count as adapter_fraction,
        bridge_count::decimal / overall_count as bridge_fraction,
        chain_of_responsibility_count::decimal / overall_count as chain_of_responsibility_fraction,
        command_count::decimal / overall_count command_fraction,
        composite_count::decimal / overall_count as composite_fraction,
        decorator_count::decimal / overall_count as decorator_fraction,
        factory_method_count::decimal / overall_count as factory_method_fraction,
        observer_count::decimal / overall_count as observer_fraction,
        prototype_count::decimal / overall_count as prototype_fraction,
        proxy_count::decimal / overall_count as proxy_fraction,
        proxy2_count::decimal / overall_count as proxy2_fraction,
        singleton_count::decimal / overall_count as singleton_fraction,
        state_count::decimal / overall_count as state_fraction,
        strategy_count::decimal / overall_count as strategy_fraction,
        template_method_count::decimal / overall_count as template_method_fraction,
        visitor_count::decimal / overall_count as visitor_fraction
    from mv_pakkages_pattern_clazz_counts
);

create unique index on mv_pakkages_pattern_clazz_fractions (pakkage_name_full);

create materialized view mv_projects_pattern_clazz_fractions as (
    select
        project_name_full,
        overall_count,
        non_pattern_count::decimal / overall_count as non_pattern_fraction,
        pattern_count::decimal / overall_count as pattern_fraction,
        adapter_count::decimal / overall_count as adapter_fraction,
        bridge_count::decimal / overall_count as bridge_fraction,
        chain_of_responsibility_count::decimal / overall_count as chain_of_responsibility_fraction,
        command_count::decimal / overall_count command_fraction,
        composite_count::decimal / overall_count as composite_fraction,
        decorator_count::decimal / overall_count as decorator_fraction,
        factory_method_count::decimal / overall_count as factory_method_fraction,
        observer_count::decimal / overall_count as observer_fraction,
        prototype_count::decimal / overall_count as prototype_fraction,
        proxy_count::decimal / overall_count as proxy_fraction,
        proxy2_count::decimal / overall_count as proxy2_fraction,
        singleton_count::decimal / overall_count as singleton_fraction,
        state_count::decimal / overall_count as state_fraction,
        strategy_count::decimal / overall_count as strategy_fraction,
        template_method_count::decimal / overall_count as template_method_fraction,
        visitor_count::decimal / overall_count as visitor_fraction
    from mv_projects_pattern_clazz_counts
);

create unique index on mv_projects_pattern_clazz_fractions (project_name_full);

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

---- FEATURES ----

create materialized view mv_projects_features as
    select
        patterns.project_name_full,
        --
        patterns.pattern_fraction > 0 as is_pattern_project,
        --
        patterns.pattern_fraction,
        --
        patterns.adapter_fraction,
        patterns.bridge_fraction,
        patterns.chain_of_responsibility_fraction,
        patterns.command_fraction,
        patterns.composite_fraction,
        patterns.decorator_fraction,
        patterns.factory_method_fraction,
        patterns.observer_fraction,
        patterns.prototype_fraction,
        patterns.proxy_fraction,
        patterns.proxy2_fraction,
        patterns.singleton_fraction,
        patterns.state_fraction,
        patterns.strategy_fraction,
        patterns.template_method_fraction,
        patterns.visitor_fraction,
        ---
        metrics.amc_avg,
        metrics.ca_avg,
        metrics.cbm_avg,
        metrics.cc_avg,
        metrics.ce_avg,
        metrics.ic_avg,
        metrics.lcom_avg,
        metrics.lcom3_avg,
        metrics.loc_avg,
        metrics.loc_sum,
        metrics.noc_avg,
        metrics.rfc_avg,
        metrics.wmc_avg,
        --
        metrics.dsc_avg,
        metrics.noh_avg,
        metrics.ana_avg,
        metrics.dam_avg,
        metrics.dcc_avg,
        metrics.cam_avg,
        metrics.moa_avg,
        metrics.mfa_avg,
        metrics.nop_avg,
        metrics.cis_avg,
        metrics.nom_avg,
        --
        metrics.reusability_avg,
        metrics.flexibility_avg,
        metrics.understandability_avg,
        metrics.functionality_avg,
        metrics.extendibility_avg,
        metrics.effectiveness_avg
    from mv_projects_pattern_clazz_fractions as patterns
    inner join mv_projects_metrics as metrics on metrics.project_name_full = patterns.project_name_full;

create unique index on mv_projects_features (project_name_full);

create materialized view mv_pakkages_features as
    select
        patterns.pakkage_name_full,
        --
        patterns.pattern_fraction > 0 as is_pattern_pakkage,
        --
        project.is_pattern_project as is_in_pattern_project,
        --
        patterns.pattern_fraction,
        --
        patterns.adapter_fraction,
        patterns.bridge_fraction,
        patterns.chain_of_responsibility_fraction,
        patterns.command_fraction,
        patterns.composite_fraction,
        patterns.decorator_fraction,
        patterns.factory_method_fraction,
        patterns.observer_fraction,
        patterns.prototype_fraction,
        patterns.proxy_fraction,
        patterns.proxy2_fraction,
        patterns.singleton_fraction,
        patterns.state_fraction,
        patterns.strategy_fraction,
        patterns.template_method_fraction,
        patterns.visitor_fraction,
        ---
        metrics.amc_avg,
        metrics.ca_avg,
        metrics.cbm_avg,
        metrics.cc_avg,
        metrics.ce_avg,
        metrics.ic_avg,
        metrics.lcom_avg,
        metrics.lcom3_avg,
        metrics.loc_avg,
        metrics.loc_sum,
        metrics.noc_avg,
        metrics.rfc_avg,
        metrics.wmc_avg,
        --
        metrics.dsc_avg,
        metrics.noh_avg,
        metrics.ana_avg,
        metrics.dam_avg,
        metrics.dcc_avg,
        metrics.cam_avg,
        metrics.moa_avg,
        metrics.mfa_avg,
        metrics.nop_avg,
        metrics.cis_avg,
        metrics.nom_avg,
        --
        metrics.reusability_avg,
        metrics.flexibility_avg,
        metrics.understandability_avg,
        metrics.functionality_avg,
        metrics.extendibility_avg,
        metrics.effectiveness_avg
    from mv_pakkages_pattern_clazz_fractions as patterns
    inner join mv_pakkages_metrics as metrics on metrics.pakkage_name_full = patterns.pakkage_name_full
    inner join mv_projects_features as project on project.project_name_full = patterns.project_name_full;

create unique index on mv_pakkages_features (pakkage_name_full);

create materialized view mv_clazzes_features as
    select
        patterns.clazz_name_full,
        --
        patterns.pattern_count > 0 as is_pattern_clazz,
        patterns.pattern_count = 1 as is_single_pattern_clazz,
        patterns.pattern_count > 1 as is_multi_pattern_clazz,
        --
        pakkage.is_pattern_pakkage as is_in_pattern_pakkage,
        pakkage.is_in_pattern_project,
        --
        patterns.pattern_count,
        --
        patterns.adapter_count,
        patterns.bridge_count,
        patterns.chain_of_responsibility_count,
        patterns.command_count,
        patterns.composite_count,
        patterns.decorator_count,
        patterns.factory_method_count,
        patterns.observer_count,
        patterns.prototype_count,
        patterns.proxy_count,
        patterns.proxy2_count,
        patterns.singleton_count,
        patterns.state_count,
        patterns.strategy_count,
        patterns.template_method_count,
        patterns.visitor_count,
        --
        metrics.amc,
        metrics.ca,
        metrics.cbm,
        metrics.cc,
        metrics.ce,
        metrics.ic,
        metrics.lcom,
        metrics.lcom3,
        metrics.loc,
        metrics.noc,
        metrics.rfc,
        metrics.wmc,
        --
        metrics.dsc,
        metrics.noh,
        metrics.ana,
        metrics.dam,
        metrics.dcc,
        metrics.cam,
        metrics.moa,
        metrics.mfa,
        metrics.nop,
        metrics.cis,
        metrics.nom,
        --
        metrics.reusability,
        metrics.flexibility,
        metrics.understandability,
        metrics.functionality,
        metrics.extendibility,
        metrics.effectiveness
    from mv_clazzes_pattern_counts as patterns
    inner join mv_clazzes_metrics as metrics on metrics.clazz_name_full = patterns.clazz_name_full
    inner join mv_pakkages_features as pakkage on pakkage.pakkage_name_full = patterns.pakkage_name_full;

create unique index on mv_clazzes_features (clazz_name_full);

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

---- DESCRIPTIVE STATISTICS ----

create materialized view mv_stat_ppc_counts as
with
    projects_total as (select count(*) as count from mv_projects_features),
    pakkages_total as (select count(*) as count from mv_pakkages_features),
    clazzes_total as (select count(*) as count from mv_clazzes_features)
select 1  as index, 'projects' as element, 'all' as pattern, count(*) as count, 100 as percent from mv_projects_features
union all
select 2, 'projects', 'non-pattern', count(*), round(count(*)::numeric / (select projects_total.count from projects_total), 4) * 100 from mv_projects_features where is_pattern_project is false
union all
select 3, 'projects', 'pattern', count(*), round(count(*)::numeric / (select projects_total.count from projects_total), 4) * 100 from mv_projects_features where is_pattern_project is true
union all
select 10, '---', '---', 0, 0
union all
select 11, 'packages', 'all', count(*), 100 from mv_pakkages_features
union all
select 12, 'packages', 'non-pattern', count(*), round(count(*)::numeric / (select pakkages_total.count from pakkages_total), 4) * 100 from mv_pakkages_features where is_pattern_pakkage is false
union all
select 13, 'packages', 'pattern', count(*), round(count(*)::numeric / (select pakkages_total.count from pakkages_total), 4) * 100 from mv_pakkages_features where is_pattern_pakkage is true
union all
select 20, '---', '---', 0, 0
union all
select 21, 'classes', 'all', count(*), 100 from mv_clazzes_features
union all
select 22, 'classes', 'non-pattern', count(*), round(count(*)::numeric / (select clazzes_total.count from clazzes_total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false
union all
select 23, 'classes', 'pattern', count(*), round(count(*)::numeric / (select clazzes_total.count from clazzes_total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true
union all
select 24, 'classes', 'single-pattern', count(*), round(count(*)::numeric / (select clazzes_total.count from clazzes_total), 4) * 100 from mv_clazzes_features where is_single_pattern_clazz is true
union all
select 25, 'classes', 'multi-pattern', count(*), round(count(*)::numeric / (select clazzes_total.count from clazzes_total), 4) * 100 from mv_clazzes_features where is_multi_pattern_clazz is true
order by index;

create materialized view mv_stat_project_counts as
with total as (select count(*) as count from mv_projects_features)
select 0 as index, 'all' as projects, count(*) as count, 100 as percent from mv_projects_features
union all
select 1, 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_projects_features where is_pattern_project is false
union all
select 2, 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_projects_features where is_pattern_project is true
order by index;

create materialized view mv_stat_pakkage_counts as
with total as (select count(*) as count from mv_pakkages_features)
select 0 as index, 'all' as pakkages, 'all' as projects, count(*) as count, 100 as percent from mv_pakkages_features
union all
select 1, 'non-pattern', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_pakkages_features where is_pattern_pakkage is false
union all
select 2, 'pattern', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_pakkages_features where is_pattern_pakkage is true
union all
select 3, 'all', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_pakkages_features where is_in_pattern_project is false
union all
select 4, 'non-pattern', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_pakkages_features where is_pattern_pakkage is false and is_in_pattern_project is false
union all
select 5, 'pattern', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_pakkages_features where is_pattern_pakkage is true and is_in_pattern_project is false
union all
select 6, 'all', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_pakkages_features where is_in_pattern_project is true
union all
select 7, 'non-pattern', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_pakkages_features where is_pattern_pakkage is false and is_in_pattern_project is true
union all
select 8, 'pattern', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_pakkages_features where is_pattern_pakkage is true and is_in_pattern_project is true
order by index;

create materialized view mv_stat_clazz_counts as
with total as (select count(*) from mv_clazzes_features)
select 0 as index, 'all' as clazzes, 'all' as pakkages, 'all' as projects, count(*) as count, 100 as percent from mv_clazzes_features
union all
select 1, 'non-pattern', 'all', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false
union all
select 2, 'pattern', 'all', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true
union all
select 3, 'all', 'non-pattern', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_in_pattern_pakkage is false
union all
select 4, 'non-pattern', 'non-pattern', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false and is_in_pattern_pakkage is false
union all
select 5, 'pattern', 'non-pattern', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true and is_in_pattern_pakkage is false
union all
select 6, 'all', 'pattern', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_in_pattern_pakkage is true
union all
select 7, 'non-pattern', 'pattern', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false and is_in_pattern_pakkage is true
union all
select 8, 'pattern', 'pattern', 'all', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true and is_in_pattern_pakkage is true
union all
select 9, 'all', 'all', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_in_pattern_project is false
union all
select 10, 'non-pattern', 'all', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false and is_in_pattern_project is false
union all
select 11, 'pattern', 'all', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true and is_in_pattern_project is false
union all
select 12, 'all', 'non-pattern', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_in_pattern_pakkage is false and is_in_pattern_project is false
union all
select 13, 'non-pattern', 'non-pattern', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false and is_in_pattern_pakkage is false and is_in_pattern_project is false
union all
select 14, 'pattern', 'non-pattern', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true and is_in_pattern_pakkage is false and is_in_pattern_project is false
union all
select 15, 'all', 'pattern', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_in_pattern_pakkage is true and is_in_pattern_project is false
union all
select 16, 'non-pattern', 'pattern', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false and is_in_pattern_pakkage is true and is_in_pattern_project is false
union all
select 17, 'pattern', 'pattern', 'non-pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true and is_in_pattern_pakkage is true and is_in_pattern_project is false
union all
select 18, 'all', 'all', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_in_pattern_project is true
union all
select 19, 'non-pattern', 'all', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false and is_in_pattern_project is true
union all
select 20, 'pattern', 'all', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true and is_in_pattern_project is true
union all
select 21, 'all', 'non-pattern', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_in_pattern_pakkage is false and is_in_pattern_project is true
union all
select 22, 'non-pattern', 'non-pattern', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false and is_in_pattern_pakkage is false and is_in_pattern_project is true
union all
select 23, 'pattern', 'non-pattern', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true and is_in_pattern_pakkage is false and is_in_pattern_project is true
union all
select 24, 'all', 'pattern', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_in_pattern_pakkage is true and is_in_pattern_project is true
union all
select 25, 'non-pattern', 'pattern', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is false and is_in_pattern_pakkage is true and is_in_pattern_project is true
union all
select 26, 'pattern', 'pattern', 'pattern', count(*), round(count(*)::numeric / (select total.count from total), 4) * 100 from mv_clazzes_features where is_pattern_clazz is true and is_in_pattern_pakkage is true and is_in_pattern_project is true
order by index;

--------------------------------------------------------------------------------
--------------------------------------------------------------------------------

with
     pi_pc_counts as (
        select pattern_id, count(distinct clazz_name_full) as count
        from mv_pattern_roles
        group by pattern_id
        order by count desc
    ),
    pc_counts as (
        select clazz_name_full, count(*) as count
        from mv_clazzes_patterns
        group by clazz_name_full
        order by count desc
    )
select 0 as index, 'all PI' as type, count(*) as count from pi_pc_counts
union
select 1, 'PI with PC = 0', count(*) from pi_pc_counts where count = 0
union
select 2, 'PI with PC > 0', count(*) from pi_pc_counts where count > 0
union
select 3, 'PI with PC = 1', count(*) from pi_pc_counts where count = 1
union
select 4, 'PI with PC > 1', count(*) from pi_pc_counts where count > 1
union
select 5, 'PI with PC = 2', count(*) from pi_pc_counts where count = 2
union
select 6, 'PI with PC = 3', count(*) from pi_pc_counts where count = 3
union
select 6, 'PI with PC > 3', count(*) from pi_pc_counts where count > 3
union
select 7, 'all PC', sum(count) from pc_counts
union
select 8, 'distinct PC', count(*) from pc_counts
order by index;

-- patterns
with total as (select 'Total' as pattern, count(*) as count, 100 as percent from mv_pattern_instances)
select (row_number() over (order by count desc) - 1) as index, *
from (
    select * from total
    union
    select pattern, count(*) as count, round(count(*)::numeric / (select total.count from total), 4) * 100
    from mv_pattern_instances
    group by pattern
 ) as results
order by count desc;

-- pattern participants
with total as (select 'Total' as pattern, count(*) as count, 100 as percent from mv_clazzes_patterns)
select (row_number() over (order by count desc) - 1) as index, *
from (
         select * from total
         union
         select pattern, count(*) as count, round(count(*)::numeric / (select total.count from total), 4) * 100
         from mv_clazzes_patterns
         group by pattern
     ) as results
order by count desc;

-- pattern participants (roles)
with total as (select 'Total' as pattern, 'Total' as role, count(*) as count, 100 as percent from mv_clazzes_pattern_roles)
select (row_number() over (order by count desc) - 1) as index, *
from (
         select * from total
         union
         select pattern, role, count(*) as count, round(count(*)::numeric / (select total.count from total), 4) * 100
         from mv_clazzes_pattern_roles
         group by pattern, role
     ) as results
order by count desc;
