from invoke import task

@task
def bump_version(ctx, part, confirm=False):
    if confirm:
        ctx.run('bumpversion {part}'.format(part=part))
    else:
        ctx.run('bumpversion --dry-run --allow-dirty --verbose {part}'.format(part=part))
        print('Add "--confirm" to actually perform the bump version.')

