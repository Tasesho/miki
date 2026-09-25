# Social Links

Social Links are directed relationships between two members of the same Discord
server. Progress belongs to the user who performs an interaction and points toward
the user who receives it.

```text
guild_id + source_user_id + target_user_id
```

The same pair of Discord users can therefore have different progress in different
servers, and the relationship in the opposite direction is independent.

## Rules

- New relationships start at level 1 with 0 XP.
- The maximum level is 10.
- The base cost is 100 XP; each following level costs twice the previous level.
- XP is cumulative. With the default base, the thresholds are 0, 100, 300, 700,
  1,500, and so on.
- The default reward is 1 XP per valid interaction.
- Bots, including Miki, cannot be Social Link targets.
- Self-relations are rejected.
- A relationship does not decay and is kept when a member leaves the server.

## XP sources

The following actions can award the configured XP amount:

- Adding a reaction to a member's message.
- Replying to a member's message.
- Directly mentioning a member.
- Giving a consumable item, once the inventory flow is connected.

Message-based interactions share these anti-abuse limits:

- At most 3 rewarded interactions per target per day.
- At most 10 rewarded message interactions globally per user per day.
- The same message can only reward one interaction for the same source and target.

Removing and re-adding a reaction does not create another reward. A reply that also
mentions the same target is counted once, as a reply.

## Commands

Users can inspect their relationships with:

```text
/social-link view
/social-link view user:@member
/social-link list
/info social-link
```

`/social-link view user:@member` shows the directed relationship from the command
author toward the selected member. `/social-link list` shows all valid targets for
the current server.

Administrators can change the XP reward for their server with:

```text
/config social-link experiencia:10
```

The same setting is also available through the generic configuration command:

```text
/config set clave:social_link_xp valor:10
```

The setting applies to reactions, replies, mentions, and consumable gifts. It is
stored in `guild_settings`, so it does not affect other servers.

## Level-up notification

When an interaction advances a relationship, Miki sends a green embed in the
channel where the interaction happened. It mentions both the source and target and
announces the new level.

## Persistence

Social Link data is stored in the shared SQLite database, but in dedicated tables:

- `social_links`: current XP and level for each directed guild relationship.
- `social_link_interactions`: idempotency, daily limits, and action history.

The schema is introduced by migrations `002_social_links.sql` and
`003_social_link_message_actions.sql`.

The implementation is split into:

- `modules/social_links.py`: Discord commands and event listeners.
- `services/social_link_service.py`: XP configuration and relationship rules.
- `repositories/social_link_repository.py`: transactions, limits, and persistence.
