import click
from click import Command


class HobbitCommand(Command):
    # https://en.wikipedia.org/wiki/ANSI_escape_code
    FOREGROUND_GREEN = '\033[32m'
    ENDC = '\033[0m'

    def format_options(self, ctx, formatter):
        """Writes all the options into the formatter if they exist."""
        # Borrowed from click.MultiCommand
        opts = []
        for param in self.get_params(ctx):
            rv = param.get_help_record(ctx)
            if rv is not None:
                # rewrite for color
                rv = list(rv)
                rv[0] = f'{self.FOREGROUND_GREEN}{rv[0]}{self.ENDC}'
                opts.append(tuple(rv))

        if opts:
            with formatter.section('Options'):
                formatter.write_dl(opts)


class CLI(click.MultiCommand, HobbitCommand):

    def list_commands(self, ctx):
        return sorted(self.cmds.keys())

    def get_command(self, ctx, cmd_name):
        try:
            return self.cmds[cmd_name]
        except KeyError:
            raise click.UsageError(click.style(
                "cmd not exist: {}\nAvailable ones are: {}".format(
                    cmd_name, ', '.join(self.cmds),
                ), fg='red'))

    @property
    def cmds(self):
        from . import bootstrap
        return {func.name: func for func in bootstrap.CMDS}

    def format_options(self, ctx, formatter):
        HobbitCommand.format_options(self, ctx, formatter)
        self.format_commands(ctx, formatter)

    def format_commands(self, ctx, formatter):
        """Extra format methods for multi methods that adds all the commands
        after the options.
        """
        # Borrowed from click.MultiCommand
        commands = []
        for subcommand in self.list_commands(ctx):
            cmd = self.get_command(ctx, subcommand)
            # What is this, the tool lied about a command.  Ignore it
            if cmd is None:
                continue
            if cmd.hidden:
                continue

            commands.append((subcommand, cmd))

        # allow for 3 times the default spacing
        if len(commands):
            limit = formatter.width - 6 - max(len(cmd[0]) for cmd in commands)

            rows = []
            for subcommand, cmd in commands:
                help = cmd.get_short_help_str(limit)
                rows.append((subcommand, help))

            if rows:
                for i, row in enumerate(rows):  # rewrite for color
                    row = list(row)
                    row[0] = f'{self.FOREGROUND_GREEN}{row[0]}{self.ENDC}'
                    rows[i] = tuple(row)
                with formatter.section('Commands'):
                    formatter.write_dl(rows)


@click.command(cls=CLI)
@click.version_option()
@click.option('--echo/--no-echo', default=False, help='Show the logs of commnad.')
@click.pass_context
def main(ctx, echo):
    if ctx.obj is None:
        ctx.obj = dict()
    ctx.obj['ECHO'] = echo


if __name__ == '__main__':
    main()
