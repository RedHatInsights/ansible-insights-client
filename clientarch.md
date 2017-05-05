# New Collector Architecture

The "new" collector is a replacement for the insights-client. The current
client is remotely controllable in a limited way. We can dictate files and
commands to run on the client machine, but cannot reliably parameterize these
collection rules. Additionally we have very little control over how to handle
sensitive data.  The new collector architecture aims to improve on all of these
points.

## Use Cases

1. Collect from a single host
2. Given an ansible inventory, collect from a set of hosts
3. Given an openstack cluster, collect from all related hosts
4. Given a RHEV cluster, collect from all related hosts
5. Given an OCP cluster, collect from all related hosts
6. Given an image id, collect from the image fs

## Environments

1. RHEL6 hosts without Ansible support
2. RHEL7 hosts without Ansible support
3. RHEL7(.4+) hosts with Ansible support
4. Unknown hosts with Ansible support (i.e. the customer has installed ansible
   on their own)
5. RHEV Hypervisors
6. RHEL Atomic Hosts

Of special note are the last two, as they often have limited write capabilities
on the given filesystem.

## Proposed Architecture

I'll go over the major components we could use to build the new collector here.

redhat-insights.rpm
- bootstrap.sh
- redhat.gpg

The job of the RPM is to give customers a single installable artifact that we
can pivot from.  The shell script (`bootstrap.sh`) would be used to fetch the
rest of our code and keep it up to date.  The gpg key would need to be shipped
in an rpm so that we can ensure that all downloaded artifacts are, indeed, Red
Hat signed.

Ansible role/module/action_plugin
- role.yml
- insights.py (action plugin)
- insights.py (module)

If Ansible is available and the customer provides an inventory (or we can
discover one) then the role and supporting parts can be used to ship our
downloadable assets to target hosts to perform collection and facilitate the
upload of information back to Red Hat.

Insights-Core.egg
- contains Specs*
- contains Shared Mappers (Parsers)
- contains Shared Reducers (Combiners)
- contains Networking code*

The bulk of the code will live in the Insights-Core.egg. Items with asterisks
are the locations where most new code will go.

Currently Specs only specify file locations and commands we wish to run, not the
means to actually execute them. In the near-ish future we will add code that
given an execution context (A host, a docker image, etc...) the spec will 'know'
how to collect it's relevant information.  This is a large project and part of
the work will be tied in with the integration of the [Vulcan
project](https://github.com/ansible/falafel-mark2) to replace the current
dependency and workflow system we have currently.

The "Networking" code is really just the parts of the current collector code
that contact Red Hat for various things and push the collected data to the
Insights service. This code doesn't *have* to be bundled within insights-core,
but it could be. The concerns to balance are project management complexity and
deployment complexity (multiple daily downloads to run collection vs a single
download)

Given the above, here's a possible work flow for the simplest case, RHEL6 host
without Ansible support:

1. invoke bootstrap.sh
   - fetch new insights.egg
   - verify signature with insights.gpg
2. invoke insights.egg:collect()
   - in the context of a single Host collect all specs
   - execute all mappers (parsers)
   - execute all reducers (combiners)
   - execute all serializers (toJson)
3. invoke insights.egg:submit()
   - post collected data to Insights service

Let's say we have ansible support, here's an example workflow:

1. invoke bootstrap.sh
  - fetch new insights.egg
  - verify signature with insights.gpg
2. invoke insights.egg:collect()
  - detect that ansible is available and that we have an inventory (or not)
    In the case we do not, we will assume localhost-only collection and provide
    that inventory
  - fetch insights role/action_plugin/module
  - install ansible components
  - invoke ansible -m insights on our inventory
  - action plugin copies insights.egg to each target
  - action plugin passes copied location to the module
  - module invokes insights.egg:collect() on its Host
  - execute all mappers (parsers), reducers (combiners), serializers (toJson)
  - return resulting json as Ansible facts
3. Action plugin invokes insights.egg:submit()
  - post collected data to Insights service
  - clean up installed Ansible components (optional)

The above examples admittedly gloss over enormous amounts of detail, but provide
a viable execution framework that will fulfill our use cases.

## Components

I want to go over some lower level components here, for two reasons:

1. provide (hopefully) long-lived terms for each
2. assign jobs to certain parts of code

### Context

A `Context` refers to the execution target type underwhich most activities will
take place. Examples are `Host` and `Image`.

### Specs

A `Spec` is a class or function that defines a single type of content and
provides a means to collect that content from a given context.

Currently we have `Spec` classes that define content, but do not gather it.
One of the major changes we'd like to implement is context-based collection
that is associated with `Spec`s directly.

### Parser

A `Parser` is class that converts varying levels of structured data into an
object representation of the data. A parser almost always will depend on a
`Spec`. Today we often refer to these classes as Shared Mappers or just Mappers.

### Combiner

A combiner is a class that depends on one or more `Parser` or `Combiner` classes
and emits a new object representation of that combination. Today we call these
Shared Reducers. In an ideal world all rules could depend only on shared
reducers as they are likely able to provide that highest level of interface for
the underlying data.

### Rule

A rule is a function (or class in the future) that evaluates any number of
Parser and Combiner outputs to determine if a Context has a particular issue.
Today we often call these reducers or plugins.

### Serializer

A serializer is a function or class that is responsible for emitting a textual
representation of a `Spec`, `Parser`, or `Combiner`. These are new components
that will be used to control what we emit from the runtime. For example, a
`Spec` serializer may simple emit the full contents of a spec whereas a
`Combiner` serializer may emit a small dictionary of information. When the new
collector asks the framework to `collect`, the final output will be a collection
of `Serializer` output documents.

### Deserializer

A deserializer is a function or class that is responsible for creating a `Spec`,
`Parser`, or `Combiner` instance from serialized output from the former.

## Known Issues

1. Scannable and LogFileMapper functions are tricky to manage because the code
   for them is stored with the rule, which we won't be shipping to customers.
   They are difficult or impossible to extract due to their dependencies.
   For this reason, we'll likely stick with the client-side filtering strategy
   we have so far for handling this data until we come up with a new system.
2. Filtering control is currently handled in the uploader.json, but the new
   client won't have such a file ultimately. As part of our build process we
   will likely need to generate the filters and bundle it with our .egg that we
   ship daily.
3. Project dependencies are expensive to accumulate because we will need to
   bundle them with our egg.  This means we will need to be very judicious with
   our dependency additions.
